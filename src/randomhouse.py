# API Docs Homepage: https://developer.penguinrandomhouse.com/docs/read/enhanced_prh_api
# Test API Endpoints Online: https://developer.penguinrandomhouse.com/io-docs
# View Available Resources: https://developer.penguinrandomhouse.com/docs/read/enhanced_prh_api/resources
import json
import os

import requests
from dotenv import load_dotenv

from config import DATA_PATH, RANDOMHOUSE_PATH, logger, timingDecorator
from utils import appendParams, loadJSON, saveJSON

load_dotenv()

API_URL = "https://api.penguinrandomhouse.com/resources/v2"
# Directory to save data
RANDOMHOUSE_API_KEY = os.getenv("RANDOMHOUSE_API_KEY")
API_DOMAIN = "ACM.CA"


@timingDecorator
def fetchBookList(
  total: int,
  increment: int = 10,
  start: int = 0,
):
  """
  Fetch list of books published within a specific year range.
  """
  if (total / increment) % 1 != 0:
    raise ValueError(
      "The total number of books must be evenly divisible by the increment."
    )

  i = 0
  current = start
  errorCount = 0
  warningCount = 0

  while (current + increment) < total:
    current = start + (i * increment)
    dumpPath = (
      f"{DATA_PATH}/randomhouse/" + f"{current}-{current + increment}_books.json"
    )

    if os.path.exists(dumpPath):
      logger.info(f"Data already exists at {dumpPath}")
      i += 1
      continue

    BASE_URL = f"{API_URL}/title/domains/{API_DOMAIN}/titles"
    params = {
      "api_key": RANDOMHOUSE_API_KEY,
      "start": current,
      "rows": increment,
      "suppressRecordCount": True,
      "returnEmptyLists": True,
      "suppressLinks": True,
      "formatFamily": ["Paperback", "Hardcover", "Ebook"],
      "zoom": [
        "https://api.penguinrandomhouse.com/title/titles/dimensions/definition",
        "https://api.penguinrandomhouse.com/title/categories/definition",
        "https://api.penguinrandomhouse.com/title/titles/awards/definition",
        "https://api.penguinrandomhouse.com/title/titles/keywords/definition",
      ],
    }
    url = appendParams(BASE_URL, params)

    try:
      response = requests.get(url)
      response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
      logger.error(f"HTTP error occurred: {http_err}")
      errorCount += 1
      continue
    except Exception as err:
      logger.error(f"Other error occurred: {err}")
      errorCount += 1
      continue

    data = response.json()
    if len(data) == 0:
      logger.warning("No data was returned for {url}")
      warningCount += 1
      continue
    saveJSON(data, dumpPath)

    logger.info(
      f"Saved movies {current}-{current + increment} to {dumpPath} [{(current - start) + increment}/{total}]"
    )

    i += 1

  logger.warning(f"Total number of warnings: {warningCount}")
  logger.error(f"Total number of errors: {errorCount}")


def cleanIncompleteFiles(increment: int):
  """
  Search for JSON files in the data/randomhouse directory that have less than `increment` titles.
  If found, delete them.
  """
  filesDeletedCount = 0

  files = sorted(os.listdir(RANDOMHOUSE_PATH), key=lambda x: int(x.split("-")[0]))
  for filename in files:
    if filename.endswith(".json"):
      path = os.path.join(RANDOMHOUSE_PATH, filename)
      if os.path.getsize(path) == 0:
        os.remove(path)
        logger.info(f"File was empty. Deleted empty file: {path}")
        filesDeletedCount += 1
        continue
      try:
        with open(path, "r") as file:
          data = json.load(file)
          if (
            "data" not in data
            or "titles" not in data["data"]
            or len(data["data"]["titles"]) < increment
          ):
            os.remove(path)
            logger.info(f"Deleted incomplete file: {path}")
            filesDeletedCount += 1
      except json.JSONDecodeError:
        os.remove(path)
        logger.info(f"Deleted corrupted file: {path}")
        filesDeletedCount += 1

  logger.info(f"Total files deleted: {filesDeletedCount}")
  if filesDeletedCount > 0:
    logger.warning("Please re-run the script to fetch the missing data.")
  return filesDeletedCount


def removeDuplicateISBNs():
  isbnList = set()
  duplicates = []

  files = sorted(os.listdir(RANDOMHOUSE_PATH), key=lambda x: int(x.split("-")[0]))
  for filename in files:
    if not filename.endswith(".json"):
      logger.warning(f"Skipping non-JSON file: {filename}")
      continue

    filteredTitles = []
    modified = False
    path = os.path.join(RANDOMHOUSE_PATH, filename)
    data = loadJSON(path)
    for book in data["data"]["titles"]:
      isbn = book["isbn"]
      if isbn in isbnList:
        data["data"]["titles"].remove(book)
        logger.info(f"Found and removed duplicate ISBN {isbn} in {path}")
        modified = True
        duplicates.append(isbn)
      else:
        isbnList.add(isbn)
        filteredTitles.append(book)

    if modified:
      data["data"]["titles"] = filteredTitles
      saveJSON(data, path)
      logger.debug(f"Saved modified data to {path}")

  logger.info(f"Total duplicates removed: {len(duplicates)}")
  return duplicates


if __name__ == "__main__":
  # Fetching 25 books is ~ 300kb. We need 300mb of data. 3 fetches ~= 1mb. 3 * 300 = 900 fetches.
  # Just to be safe, multiply that by 5. Therefore, we make 4500 fetches for 112,500 (9000 * 25) books.
  INCREMENT = 25
  TOTAL_BOOKS = 4500 * INCREMENT

  fetchBookList(TOTAL_BOOKS, increment=INCREMENT)

  cleanIncompleteFiles(INCREMENT)

  duplicates = removeDuplicateISBNs()
