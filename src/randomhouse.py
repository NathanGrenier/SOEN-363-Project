# API Docs Homepage: https://developer.penguinrandomhouse.com/docs/read/enhanced_prh_api

# Test API Endpoints Online: https://developer.penguinrandomhouse.com/io-docs

# View Available Resources: https://developer.penguinrandomhouse.com/docs/read/enhanced_prh_api/resources

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = "https://api.penguinrandomhouse.com/resources/v2"
DUMP_DATA_PATH = "./dump/raw_data/randomhouse/"
API_KEY = os.getenv("RANDOMHOUSE_API_KEY")
API_DOMAIN = "PRH.US"  # We'll only consider the US domain (books available in the US).


def test():
  response = requests.get(
    f"{API_URL}/title/domains/{API_DOMAIN}/works?api_key={API_KEY}",
  )
  try:
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    print(json.dumps(data, indent=2))
  except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
  except requests.exceptions.RequestException as req_err:
    print(f"Request error occurred: {req_err}")
  except json.JSONDecodeError as json_err:
    print(f"JSON decode error occurred: {json_err}")
    print(f"Response content: {response.text}")


if __name__ == "__main__":
  launches = test()
