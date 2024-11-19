import logging
import os

import psycopg

from config import (
  GOOGLEBOOKS_PATH,
  POSTGRES_CONFIG,
  PREPARED_PATH,
  RANDOMHOUSE_PATH,
  logger,
)
from googlebooks import fetchAllBookDetails
from randomhouse import fetchBookList
from utils import loadJSON, saveJSON


def prepareBookData(bookList, failedISBNs):
  PHYSICAL_BOOKS = ["Hardcover", "Paperback"]

  preparedData = []
  for book in bookList:
    data = {}
    isbn = book["isbn"]
    if isbn in failedISBNs:
      logger.warning(f"Skipping failed ISBN: {isbn}")
      continue

    googleBooksPath = f"{GOOGLEBOOKS_PATH}/{isbn}_details.json"
    # logger.debug(f"Loading data from {googleBooksPath}")
    googleBooksData = loadJSON(googleBooksPath)["items"][0]

    publisher = (
      googleBooksData["volumeInfo"]["publisher"]
      if "publisher" in googleBooksData["volumeInfo"]
      else book["publisher"]["description"]
    )

    awards = [
      {
        "name": award["description"],
        "level": award["level"],
        "year": award["year"],
      }
      for award in book["_embeds"][2]["awards"]
    ]

    categories = [
      category["description"] for category in book["_embeds"][1]["categories"]
    ]

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
      "publishedDate": googleBooksData["volumeInfo"]["publishedDate"],
      "description": googleBooksData["volumeInfo"]["description"],
      "pageCount": googleBooksData["volumeInfo"]["pageCount"],
      "averageRating": googleBooksData["volumeInfo"].get("averageRating", None),
      "ratingCount": googleBooksData["volumeInfo"].get("ratingsCount", None),
      "language": googleBooksData["volumeInfo"]["language"],
      "isPhysical": True if book["formatFamily"] in PHYSICAL_BOOKS else False,
      "authors": googleBooksData["volumeInfo"]["authors"],
      "keywords": book["_embeds"][3]["keywords"][0].split(";")
      if len(book["_embeds"][3]["keywords"]) > 0
      else None,
      "awards": awards if len(awards) > 0 else None,
      "categories": categories if len(categories) > 0 else None,
      "prices": prices,
    }

    if data["isPhysical"]:
      data["coverType"] = book["formatFamily"]
      data["dimensions"] = book["_embeds"][0]["dimensions"]
    else:
      data["viewability"] = book["accessInfo"]["viewability"]
      data["webReaderLink"] = (
        book["accessInfo"]["webReaderLink"]
        if book["accessInfo"]["webReaderLink"]
        else None
      )

    preparedData.append(data)

  return preparedData


def prepareAllBookData(PREPARED_DATA_MAX_SIZE: int):
  preparedBooks = []
  totalProcessedBooks = 0

  files = sorted(os.listdir(RANDOMHOUSE_PATH), key=lambda x: int(x.split("-")[0]))
  for filename in files:
    logger.debug(f"Reading data from {filename}")

    if not filename.endswith(".json"):
      logger.warning(f"Skipping non-JSON file: {filename}")
      continue

    path = os.path.join(RANDOMHOUSE_PATH, filename)
    data = loadJSON(path)

    preparedData = prepareBookData(data["data"]["titles"], failedISBNs)
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
  cursor.execute("SELECT A_ID FROM director WHERE A_NAME = %s", (author,))
  row = cursor.fetchone()

  if row:
    return row[0]
  else:
    cursor.execute("INSERT INTO Author (A_NAME) VALUES (%s) RETURNING A_ID", (author,))
    logger.debug(f"Created new Author: {author}")
    return cursor.fetchone()[0]


def insertBook(bookData, conn):
  cursor = conn.cursor()

  # Create new author if it doesn't exist (and return the new id)
  authorIds = []
  for author in bookData["authors"]:
    authorIds.append(createNewAuthor(cursor, author))

  # Insert book
  cursor.execute(
    """
      INSERT INTO Book (B_TITLE, B_SUBTITLE, B_ISBN13, B_ISBN10, B_PUBLISHER, B_PUBLISH_DATE, B_DESCRIPTION, B_PAGE_COUNT, B_AVERAGE_RATING, B_RATING_COUNT, B_LANGUAGE, B_IS_PHYSICAL)
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      RETURNING M_ID
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

  cursor.close()


if __name__ == "__main__":
  logger.setLevel(logging.DEBUG)

  # Fetching 25 books is ~ 300kb. We need 300mb of data. 3 fetches ~= 1mb. 3 * 300 = 900 fetches.
  # Just to be safe, multiply that by 5. Therefore, we make 4500 fetches for 112,500 (9000 * 25) books.
  INCREMENT = 25
  TOTAL_BOOKS = 4500 * INCREMENT

  # fetchBookList(TOTAL_BOOKS, increment=INCREMENT)

  failedISBNs = fetchAllBookDetails(INCREMENT)

  PREPARED_DATA_MAX_SIZE = 5000

  prepareAllBookData(PREPARED_DATA_MAX_SIZE)

  # TODO: Insert prepared data into PostgreSQL database
  with psycopg.connect(**POSTGRES_CONFIG) as conn:
    for filename in os.listdir(PREPARED_PATH):
      if not filename.endswith(".json"):
        logger.warning(f"Skipping non-JSON file: {filename}")
        continue

      path = os.path.join(PREPARED_PATH, filename)
      preparedBooks = loadJSON(path)

      for book in preparedBooks:
        insertBook(book, conn)
        logger.debug(f"Inserted book: {book['ISBN13']}")
  logger.info("All books inserted into the database.")
