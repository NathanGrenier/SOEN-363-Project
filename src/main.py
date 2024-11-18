import json
import logging
import os

from config import configureLogger
from googlebooks import getBookDetails
from randomhouse import fetchBookList

DATA_PATH = ".src/data/"

logger = configureLogger("logger", LEVEL=logging.DEBUG)

if __name__ == "__main__":
  fetchBookList()
