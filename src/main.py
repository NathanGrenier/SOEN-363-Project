import json
import logging
import os

from config import configureLogger
from googlebooks import fetchAllBookDetails
from randomhouse import fetchBookList

DATA_PATH = ".src/data/"

logger = configureLogger("logger", LEVEL=logging.DEBUG)

if __name__ == "__main__":
  # Fetching 25 books is ~ 300kb. We need 300mb of data. 3 fetches ~= 1mb. 3 * 300 = 900 fetches.
  # Just to be safe, multiply that by 5. Therefore, we make 4500 fetches for 112,500 (9000 * 25) books.
  INCREMENT = 25
  TOTAL_BOOKS = 4500 * INCREMENT

  fetchBookList(TOTAL_BOOKS, increment=INCREMENT)

  failedISBNs = fetchAllBookDetails()

  # TODO: Prepare the data. Make sure to exclude failed ISBNs
