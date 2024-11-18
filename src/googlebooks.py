import json
import os

import requests
from dotenv import load_dotenv

from config import logger, timingDecorator
from utils import appendParams, saveJSON

load_dotenv()

API_URL = "https://www.googleapis.com/books/v1"
# Directory to save data
DATA_PATH = "./data"


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

  MAX_RETRIES = 5
  for attempt in range(MAX_RETRIES):
    try:
      response = requests.get(url)
      response.raise_for_status()
      break
    except requests.exceptions.HTTPError as http_err:
      logger.warning(
        f"HTTP error occurred: {http_err} - Attempt {attempt + 1} of {MAX_RETRIES}"
      )
    except Exception as err:
      logger.warning(
        f"Other error occurred: {err} - Attempt {attempt + 1} of {MAX_RETRIES}"
      )
    if attempt == MAX_RETRIES - 1:
      logger.error(f"Failed to get data for {ISBN} with request URL: {url}")
      return ISBN

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
  RANDOMHOUSE_PATH = f"{DATA_PATH}/randomhouse"

  totalBookCount = 0
  failedISBNs = set()

  files = sorted(os.listdir(RANDOMHOUSE_PATH), key=lambda x: int(x.split("-")[0]))
  for filename in files:
    if filename.endswith(".json"):
      path = os.path.join(RANDOMHOUSE_PATH, filename)
      with open(path, "r") as file:
        logger.debug(f"Reading data from {path}")
        data = json.load(file)
        totalBookCount += increment

        for item in data["data"]["titles"]:
          isbn = item["isbn"]

          dumpPath = f"{DATA_PATH}/googlebooks/" + f"{isbn}_details.json"
          if os.path.exists(dumpPath):
            logger.info(f"Data for {isbn}_details already exists at {dumpPath}")
            continue

          result = getBookDetails(isbn)
          if result != "Success":
            failedISBNs.add(result)

    # For testing small amounts of requests
    # if totalBookCount >= 100:
    #   break

  if len(failedISBNs) > 0:
    logger.error(f"Failed to get data for {len(failedISBNs)}/{totalBookCount} books.")

    failedISBNsPath = f"{DATA_PATH}/failed-isbns.json"
    with open(failedISBNsPath, "w") as file:
      json.dump(list(failedISBNs), file, indent=4)
    logger.info(f"Saved failed ISBNs to {failedISBNsPath}")

  return failedISBNs


if __name__ == "__main__":
  fetchAllBookDetails()
