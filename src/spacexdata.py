import json

import requests

API_URL = "https://api.spacexdata.com/v4"


def getLaunches():
  URL = API_URL + "/launches/query"
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
    totalPages = data["totalPages"]
    print(f"Page: {page}/{totalPages}")
    print(json.dumps(data, indent=2))
    print("\n")
    hasMore = data["hasNextPage"]
    page += 1


if __name__ == "__main__":
  getLaunches()
