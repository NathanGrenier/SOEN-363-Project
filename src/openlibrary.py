import json

import requests

API_URL = "https://openlibrary.org/"
DUMP_DATA_PATH = "./dump/raw_data/"


def getLaunches():
  URL = API_URL + "/launches/query"
  all_launches = []
  hasMore = True
  page = 1
  while hasMore:
    response = requests.post(
      URL,
      json={
        "query": {},
        "options": {
          "pagination": True,
          "page": page,
          "limit": 10,
          "select": ["name", "date_utc"],
        },
      },
    )
    data = response.json()
    all_launches.extend(data["docs"])
    hasMore = data["hasNextPage"]
    page += 1

  dumpPath = DUMP_DATA_PATH + "launches.json"
  with open(dumpPath, "w") as f:
    json.dump(all_launches, f)


if __name__ == "__main__":
  launches = getLaunches()
