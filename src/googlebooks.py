import json
import os
import time  # Add this import

import requests
from dotenv import load_dotenv

from config import DATA_PATH, RANDOMHOUSE_PATH, logger, timingDecorator
from utils import appendParams, loadJSON, saveJSON

load_dotenv()

API_URL = "https://www.googleapis.com/books/v1"
# Directory to save data


def getBookDetails(ISBN):
  dumpPath = f"{DATA_PATH}/googlebooks/" + f"{ISBN}_details.json"

  if os.path.exists(dumpPath):
    logger.info(f"Data for book ({ISBN}) already exists at {dumpPath}")
    return dumpPath

  params = {
    "q": f"isbn:{ISBN}",
    "projection": "full",
  }

  BASE_URL = f"{API_URL}/volumes"
  url = appendParams(BASE_URL, params)

  MAX_RETRIES = 6
  for attempt in range(MAX_RETRIES):
    try:
      response = requests.get(url)
      response.raise_for_status()
      break
    except requests.exceptions.HTTPError as http_err:
      if response.status_code == 429:
        logger.warning(
          f"HTTP error occurred: {http_err} - Attempt {attempt + 1} of {MAX_RETRIES}. Retrying after delay."
        )
        time.sleep(2**attempt)  # Exponential backoff
      else:
        logger.warning(
          f"HTTP error occurred: {http_err} - Attempt {attempt + 1} of {MAX_RETRIES}"
        )
    except Exception as err:
      logger.warning(
        f"Other error occurred: {err} - Attempt {attempt + 1} of {MAX_RETRIES}"
      )
    if attempt == MAX_RETRIES - 1:
      logger.error(f"Failed to get data for {ISBN} with request URL: {url}")
      return "RateLimited"

  data = response.json()

  totalItems = data.get("totalItems", 0)
  if totalItems == 0:
    logger.error(f"No data was returned for book ({ISBN}).")
    return ISBN

  saveJSON(data, dumpPath)

  logger.info(f"Saved book ({ISBN}) details to {dumpPath}")
  return "Success"


@timingDecorator
def fetchAllBookDetails(increment: int):
  totalBookCount = 0
  failedISBNs = set()
  rateLimitedISBNs = set()

  files = sorted(os.listdir(RANDOMHOUSE_PATH), key=lambda x: int(x.split("-")[0]))
  for filename in files:
    if filename.endswith(".json"):
      path = os.path.join(RANDOMHOUSE_PATH, filename)

      logger.debug(f"Reading data from {path}")
      data = loadJSON(path)
      totalBookCount += increment

      for item in data["data"]["titles"]:
        isbn = item["isbn"]

        dumpPath = f"{DATA_PATH}/googlebooks/" + f"{isbn}_details.json"
        if os.path.exists(dumpPath):
          logger.info(f"Data for {isbn}_details already exists at {dumpPath}")
          continue

        result = getBookDetails(isbn)
        if result == "RateLimited":
          rateLimitedISBNs.add(isbn)
        elif result != "Success":
          failedISBNs.add(result)

  if len(failedISBNs) > 0:
    logger.error(f"Failed to get data for {len(failedISBNs)}/{totalBookCount} books.")

    failedISBNsPath = f"{DATA_PATH}/failed-isbns.json"
    with open(failedISBNsPath, "w") as file:
      json.dump(list(failedISBNs), file, indent=4)
    logger.info(f"Saved failed ISBNs to {failedISBNsPath}")

  if len(rateLimitedISBNs) > 0:
    logger.error(
      f"Rate limited while getting data for {len(rateLimitedISBNs)}/{totalBookCount} books."
    )

    rateLimitedISBNsPath = f"{DATA_PATH}/ratelimited-isbns.json"
    with open(rateLimitedISBNsPath, "w") as file:
      json.dump(list(rateLimitedISBNs), file, indent=4)
    logger.info(f"Saved rate limited ISBNs to {rateLimitedISBNsPath}")

  return (failedISBNs, rateLimitedISBNs)


if __name__ == "__main__":
  RANDOMHOUSE_INCREMENT = 25

  failedISBNs, rateLimitedISBNs = fetchAllBookDetails(RANDOMHOUSE_INCREMENT)
