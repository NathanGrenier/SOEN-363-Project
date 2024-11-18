# API Docs Homepage: https://developer.penguinrandomhouse.com/docs/read/enhanced_prh_api
# Test API Endpoints Online: https://developer.penguinrandomhouse.com/io-docs
# View Available Resources: https://developer.penguinrandomhouse.com/docs/read/enhanced_prh_api/resources
import os

import requests
from dotenv import load_dotenv

from config import logger, timingDecorator
from utils import appendParams, saveJSON

load_dotenv()

API_URL = "https://api.penguinrandomhouse.com/resources/v2"
# Directory to save data
DATA_PATH = "./data"
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


if __name__ == "__main__":
  # Fetching 25 books is ~ 300kb. We need 300mb of data. 3 fetches ~= 1mb. 3 * 300 = 900 fetches.
  # Just to be safe, multiply that by 5. Therefore, we make 4500 fetches for 112,500 (9000 * 25) books.
  INCREMENT = 25
  TOTAL_BOOKS = 4500 * INCREMENT

  fetchBookList(TOTAL_BOOKS, increment=INCREMENT)
