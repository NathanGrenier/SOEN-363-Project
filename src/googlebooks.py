import json
import logging
import os

import requests
from dotenv import load_dotenv

from config import configureLogger, timingDecorator
from utils import appendParams, saveJSON

load_dotenv()

API_URL = "https://www.googleapis.com/books/v1"
# Directory to save data
DATA_PATH = "./data"

logger = configureLogger("logger", LEVEL=logging.DEBUG)


@timingDecorator
def getBookDetails(ISBN):
  """
  Get the details of a movie from the Free-Movie DB API.
  """
  dumpPath = f"{DATA_PATH}/googlebooks/" + f"{ISBN}_details.json"

  if os.path.exists(dumpPath):
    logger.info(f"Data for book ({ISBN}) already exists at {dumpPath}")
    return dumpPath

  params = {
    "q": ISBN,
    "projection": "full",
  }

  BASE_URL = f"{API_URL}/volumes"
  url = appendParams(BASE_URL, params)

  response = requests.get(url)
  response.raise_for_status()

  data = response.json()
  saveJSON(data, dumpPath)

  logger.info(f"Saved book ({ISBN}) details to {dumpPath}")
  return dumpPath
