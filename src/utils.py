import json
import os


def appendParams(url, params, first=True):
  """
  Append query parameters to a URL.
  """
  for key, value in params.items():
    if isinstance(value, list):
      for item in value:
        if first:
          url += f"?{key}={item}"
          first = False
        else:
          url += f"&{key}={item}"
      continue
    else:
      if first:
        url += f"?{key}={value}"
        first = False
      else:
        url += f"&{key}={value}"
  return url


def saveJSON(data, dumpPath):
  """
  Save JSON data to a file.
  """
  os.makedirs(os.path.dirname(dumpPath), exist_ok=True)
  with open(dumpPath, "w") as f:
    json.dump(data, f, indent=2)


def loadJSON(file_path):
  """
  Load a JSON file and return the data as a Python object.

  :param file_path: Path to the JSON file.
  :return: Python object representing the JSON data.
  """
  with open(file_path, "r") as file:
    data = json.load(file)
  return data
