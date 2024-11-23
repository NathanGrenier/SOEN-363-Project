import json
import logging
import os
from datetime import datetime

import psycopg

from config import (
  GOOGLEBOOKS_PATH,
  POSTGRES_CONFIG,
  PREPARED_PATH,
  RANDOMHOUSE_PATH,
  logger,
)
from googlebooks import fetchAllBookDetails
from randomhouse import cleanIncompleteFiles, fetchBookList, removeDuplicateISBNs
from utils import loadJSON, saveJSON


def prepareBookData(bookList, failedISBNs: set = set(), rateLimitedISBNs: set = set()):
  PHYSICAL_BOOKS = ["Hardcover", "Paperback"]

  preparedData = []
  for book in bookList:
    data = {}
    isbn = book["isbn"]
    logger.debug(f"Preparing data for ISBN: {isbn}")
    if isbn in failedISBNs:
      logger.warning(f"Skipping failed ISBN: {isbn}")
      continue
    elif isbn in rateLimitedISBNs:
      logger.warning(f"Skipping failed ISBN (due to rate limiting): {isbn}")
      continue

    googleBooksPath = f"{GOOGLEBOOKS_PATH}/{isbn}_details.json"
    # logger.debug(f"Loading data from {googleBooksPath}")
    googleBooksData = loadJSON(googleBooksPath)["items"][0]

    publisher = (
      googleBooksData["volumeInfo"]["publisher"]
      if "publisher" in googleBooksData["volumeInfo"]
      else book["publisher"]["description"]
    )

    publishDate = (
      googleBooksData["volumeInfo"]["publishedDate"]
      if "publishedDate" in googleBooksData["volumeInfo"]
      else book["onsale"]
    )
    # Ensure publishDate is in the correct format
    try:
      publishDate = datetime.strptime(publishDate, "%Y-%m-%d").date()
    except ValueError:
      try:
        publishDate = datetime.strptime(publishDate, "%Y-%m").date()
      except ValueError:
        try:
          publishDate = datetime.strptime(publishDate, "%Y").date()
        except ValueError:
          logger.warning(f"Invalid publish date format for ISBN: {isbn}")
          publishDate = None
    if publishDate:
      publishDate = publishDate.isoformat()

    if "description" in googleBooksData["volumeInfo"]:
      description = googleBooksData["volumeInfo"]["description"]
    else:
      description = ""

    pageCount = (
      googleBooksData["volumeInfo"]["pageCount"]
      if "pageCount" in googleBooksData["volumeInfo"]
      else book["pages"]
    )

    authors = (
      googleBooksData["volumeInfo"]["authors"]
      if "authors" in googleBooksData["volumeInfo"]
      else book["author"]
    )
    if not isinstance(authors, list):
      authors = [authors]

    awards = [
      {
        "name": award["description"],
        "level": award["level"],
        "year": award["year"],
      }
      for award in book["_embeds"][2]["awards"]
    ]

    # Remove duplicates using set
    categories = list(
      {category["description"] for category in book["_embeds"][1]["categories"]}
    )

    prices = [
      {"amount": price["amount"], "currencyCode": price["currencyCode"]}
      for price in book["price"]
    ]

    data = {
      "title": book["title"],
      "subtitle": book["subtitle"],
      "ISBN13": isbn,
      "ISBN10": book["isbn10"],
      "publisher": publisher,
      "publishedDate": publishDate,
      "description": description,
      "pageCount": pageCount,
      "averageRating": googleBooksData["volumeInfo"].get("averageRating", None),
      "ratingCount": googleBooksData["volumeInfo"].get("ratingsCount", None),
      "language": googleBooksData["volumeInfo"]["language"],
      "isPhysical": True if book["formatFamily"] in PHYSICAL_BOOKS else False,
      "authors": authors,
      "keywords": book["_embeds"][3]["keywords"][0].split(";")
      if len(book["_embeds"][3]["keywords"]) > 0
      else [],
      "awards": awards,
      "categories": categories,
      "prices": prices,
    }

    if data["isPhysical"]:
      data["coverType"] = book["formatFamily"]
      data["dimensions"] = book["_embeds"][0]["dimensions"]
    else:
      data["viewability"] = googleBooksData["accessInfo"]["viewability"]
      data["webReaderLink"] = (
        googleBooksData["accessInfo"]["webReaderLink"]
        if "webReaderLink" in googleBooksData["accessInfo"]
        else None
      )

    preparedData.append(data)

  return preparedData


def prepareAllBookData(
  PREPARED_DATA_MAX_SIZE: int, failedISBNs: set = set(), rateLimitedISBNs: set = set()
):
  preparedBooks = []
  totalProcessedBooks = 0

  files = sorted(os.listdir(RANDOMHOUSE_PATH), key=lambda x: int(x.split("-")[0]))
  for filename in files:
    logger.info(f"Reading data from {filename}")

    if not filename.endswith(".json"):
      logger.warning(f"Skipping non-JSON file: {filename}")
      continue

    path = os.path.join(RANDOMHOUSE_PATH, filename)
    data = loadJSON(path)

    preparedData = prepareBookData(
      data["data"]["titles"], failedISBNs, rateLimitedISBNs
    )
    preparedBooks.extend(preparedData)

    while len(preparedBooks) >= PREPARED_DATA_MAX_SIZE:
      savePath = f"{PREPARED_PATH}/{totalProcessedBooks}-{totalProcessedBooks + PREPARED_DATA_MAX_SIZE}_prepared_books.json"
      logger.info(f"Saving {PREPARED_DATA_MAX_SIZE} prepared books to {savePath}")

      # Save first PREPARED_DATA_MAX_SIZE books
      saveJSON(preparedBooks[:PREPARED_DATA_MAX_SIZE], savePath)

      # Keep the remaining books for next iteration
      preparedBooks = preparedBooks[PREPARED_DATA_MAX_SIZE:]
      totalProcessedBooks += PREPARED_DATA_MAX_SIZE

  # Save any remaining books
  if preparedBooks:
    savePath = f"{PREPARED_PATH}/{totalProcessedBooks}-{totalProcessedBooks + len(preparedBooks)}_prepared_books.json"
    logger.info(f"Saving remaining {len(preparedBooks)} prepared books to {savePath}")
    saveJSON(preparedBooks, savePath)


def createNewAuthor(cursor, author):
  cursor.execute("SELECT A_ID FROM Author WHERE A_NAME = %s", (author,))
  row = cursor.fetchone()

  if row:
    return row[0]
  else:
    cursor.execute("INSERT INTO Author (A_NAME) VALUES (%s) RETURNING A_ID", (author,))
    # logger.debug(f"Created new Author: {author}")
    return cursor.fetchone()[0]


def createNewCategory(cursor, category):
  cursor.execute("SELECT C_ID FROM Category WHERE C_NAME = %s", (category,))
  row = cursor.fetchone()

  if row:
    return row[0]
  else:
    cursor.execute(
      "INSERT INTO Category (C_NAME) VALUES (%s) RETURNING C_ID", (category,)
    )
    # logger.debug(f"Created new Category: {category}")
    return cursor.fetchone()[0]


def insertBook(bookData, conn):
  cursor = conn.cursor()

  # Create new author if it doesn't exist (and return the new id)
  authorIds = []
  for author in bookData["authors"]:
    authorIds.append(createNewAuthor(cursor, author))

  # Create new category if it doesn't exist (and return the new id)
  categoryIds = []
  for category in bookData["categories"]:
    categoryIds.append(createNewCategory(cursor, category))

  # Insert book
  cursor.execute(
    """
      INSERT INTO Book (B_TITLE, B_SUBTITLE, B_ISBN13, B_ISBN10, B_PUBLISHER, B_PUBLISH_DATE, B_DESCRIPTION, B_PAGE_COUNT, B_AVERAGE_RATING, B_RATING_COUNT, B_LANGUAGE, B_IS_PHYSICAL)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      RETURNING B_ID
      """,
    (
      bookData["title"],
      bookData["subtitle"],
      bookData["ISBN13"],
      bookData["ISBN10"],
      bookData["publisher"],
      bookData["publishedDate"],
      bookData["description"],
      bookData["pageCount"],
      bookData["averageRating"],
      bookData["ratingCount"],
      bookData["language"],
      bookData["isPhysical"],
    ),
  )
  bookId = cursor.fetchone()[0]

  # Insert bookAuthors
  for authorId in authorIds:
    cursor.execute(
      "INSERT INTO Book_Author (B_ID, A_ID) VALUES (%s, %s)", (bookId, authorId)
    )

  # Insert bookCategories
  for categoryId in categoryIds:
    cursor.execute(
      "INSERT INTO Book_Category (B_ID, C_ID) VALUES (%s, %s)", (bookId, categoryId)
    )

  # Insert bookPrices. TODO: Handle unsupported currencies
  for price in bookData["prices"]:
    cursor.execute(
      "INSERT INTO Price (B_ID, P_PRICE, P_CURRENCY) VALUES (%s, %s, %s)",
      (bookId, price["amount"], price["currencyCode"]),
    )

  # Insert bookAwards
  for award in bookData["awards"]:
    cursor.execute(
      "INSERT INTO Award (B_ID, AW_NAME, AW_YEAR, AW_LEVEL) VALUES (%s, %s, %s, %s)",
      (bookId, award["name"], award["year"], award["level"]),
    )

  # Insert keywords
  for keyword in bookData["keywords"]:
    cursor.execute(
      "INSERT INTO Keywords (B_ID, K_NAME) VALUES (%s, %s)", (bookId, keyword)
    )

  # Insert book type and related details
  if bookData["isPhysical"]:
    cursor.execute(
      "INSERT INTO Physical_Book (B_ID, PB_COVER_TYPE, PB_LENGTH, PB_WIDTH, PB_DEPTH, PB_WEIGHT) VALUES (%s, %s, %s, %s, %s, %s)",
      (
        bookId,
        bookData["coverType"],
        bookData["dimensions"]["length"],
        bookData["dimensions"]["width"],
        bookData["dimensions"]["depth"],
        bookData["dimensions"]["grossWeight"],
      ),
    )
  else:
    cursor.execute(
      "INSERT INTO EBook (B_ID, EB_VIEWABILITY, EB_WEB_READER_LINK) VALUES (%s, %s, %s)",
      (bookId, bookData["viewability"], bookData["webReaderLink"]),
    )

  cursor.close()


def loadInsertionProgress():
  """Load the last successfully processed file from progress tracker."""
  try:
    with open("./data/insertion-progress.json", "r") as f:
      return json.load(f)
  except FileNotFoundError:
    return {"lastCompletedFile": None}


def saveInsertionProgress(filename):
  """Save the last successfully processed file."""
  with open("./data/insertion-progress.json", "w") as f:
    json.dump({"lastCompletedFile": filename}, f)


def insertPreparedBooks():
  progress = loadInsertionProgress()
  lastCompleted = progress["lastCompletedFile"]

  with psycopg.connect(**POSTGRES_CONFIG) as conn:
    sortedPreparedFiles = sorted(
      os.listdir(PREPARED_PATH), key=lambda x: int(x.split("-")[0])
    )

    # Find the starting point
    startIdx = 0
    try:
      startIdx = sortedPreparedFiles.index(lastCompleted) + 1
      logger.info(f"Resuming from file after: {lastCompleted}")
    except ValueError:
      logger.warning(
        f"Previously recorded file {lastCompleted} not found. Starting from beginning."
      )

    # Process each file
    for filename in sortedPreparedFiles[startIdx:]:
      if not filename.endswith(".json"):
        logger.warning(f"Skipping non-JSON file: {filename}")
        continue

      logger.info(f"Reading prepared books from {filename}")

      try:
        # Start transaction for the entire file
        with conn.transaction():
          path = os.path.join(PREPARED_PATH, filename)
          preparedBooks = loadJSON(path)

          for book in preparedBooks:
            try:
              logger.debug(f"Inserting book: {book['ISBN13']}")
              insertBook(book, conn)
            except Exception as e:
              logger.error(
                f"Failed to insert book {book['ISBN13']} from file {filename}: {str(e)}"
              )
              raise  # Re-raise to trigger transaction rollback

          saveInsertionProgress(filename)
          logger.info(f"Successfully completed file: {filename}")
      except Exception:
        conn.rollback()
        raise  # Re-raise to stop processing

    logger.info("All books inserted into the database.")


if __name__ == "__main__":
  logger.setLevel(logging.DEBUG)
  RE_FETCH = False
  RE_PREPARE = False

  # Fetching 25 books is ~ 300kb. We need 300mb of data. 3 fetches ~= 1mb. 3 * 300 = 900 fetches.
  # Just to be safe, multiply that by 5. Therefore, we make 4500 fetches for 112,500 (9000 * 25) books.
  INCREMENT = 25
  TOTAL_BOOKS = 4500 * INCREMENT

  PREPARED_DATA_MAX_SIZE = 5000
  if RE_FETCH:
    fetchBookList(TOTAL_BOOKS, increment=INCREMENT)
    cleanIncompleteFiles(INCREMENT)
    removeDuplicateISBNs()

    failedISBNs, rateLimitedISBNs = fetchAllBookDetails(INCREMENT)
  else:
    failedISBNs = loadJSON("./data/failed-isbns.json")
    rateLimitedISBNs = loadJSON("./data/ratelimited-isbns.json")

  if RE_PREPARE:
    prepareAllBookData(PREPARED_DATA_MAX_SIZE, failedISBNs, rateLimitedISBNs)

  try:
    insertPreparedBooks()
  except Exception as e:
    logger.error(f"Database insertion process failed: {str(e)}")
    logger.info("You can restart the script to resume from the last successful file.")
