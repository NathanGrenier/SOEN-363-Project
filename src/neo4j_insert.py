import logging

import pandas as pd

from config import DATA_DUMP_PATH, NEO4J_CONFIG, logger
from neo4j import GraphDatabase


def execute_cypher_query(driver, queryFile):
  """
  Execute Cypher queries stored in a .cypher file.

  Args:
      driver (neo4j.GraphDatabase.driver): Neo4j driver object
      queryFile (str): Path to the .cypher file containing the queries
  """
  with open(queryFile, "r") as f:
    queries = f.read().split(";")

  for query in queries:
    query = query.strip()
    if query:
      logger.debug(f"Executing query: {query}")
      result, summary, _ = driver.execute_query(query, database_="neo4j")

  logger.debug(f"Executed all queries from {queryFile}")


def importAuthors(driver, chunkSize=1000):
  logger.info("Importing authors...")
  with driver.session() as session:
    logger.debug("Loading author data from CSV...")
    authorDumpPath = f"{DATA_DUMP_PATH}/author.csv"
    csvReader = pd.read_csv(authorDumpPath, chunksize=chunkSize)

    # Calculate total number of authors for progress tracking
    totalAuthors = pd.read_csv(authorDumpPath).shape[0]
    authorsProcessed = 0
    failedAuthors = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            if (
              pd.isna(row["a_name"]) or not row["a_name"]
            ):  # Skip if author name is NaN or empty
              logger.debug(
                f"Skipping author (id={row['a_id']}) with NaN or empty name at index {index}"
              )
              continue
            try:
              tx.run(
                """MERGE (:Author {id: $a_id, name: $a_name})""",
                a_id=int(row["a_id"]),
                a_name=row["a_name"],
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to import author: {{Index={index}, ID={row['a_id']}, Name={row['a_name']}}} Error: {str(row_error)}"
              )
              failedAuthors += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            authorsProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {authorsProcessed}/{totalAuthors} authors processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing author chunk: {str(chunk_error)}")

    logger.info(
      f"Author import completed: {authorsProcessed}/{totalAuthors} authors processed"
    )
    if failedAuthors > 0:
      logger.error(f"A total of {failedAuthors} authors failed to import")


def importCategories(driver, chunkSize=1000):
  logger.info("Importing categories...")
  with driver.session() as session:
    logger.debug("Loading category data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/category.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """MERGE (:Category {id: $c_id, name: $c_name})""",
                c_id=int(row["c_id"]),
                c_name=row["c_name"],
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to execute with: {{Index={index}, c_id={row['c_id']}, c_name={row['c_name']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} categories processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Category import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(f"A total of {totalFailed} categories failed to import")


def createCurrencyTypes(driver):
  logger.debug("Loading price data from CSV...")
  dumpPath = f"{DATA_DUMP_PATH}/price.csv"
  prices = pd.read_csv(dumpPath)
  uniqueCurrencies = prices["p_currency"].unique()

  logger.info("Creating Currency Types...")
  for currency in uniqueCurrencies:
    driver.execute_query(
      f"MERGE (:CurrencyType {{name: '{currency}'}})", database_="neo4j"
    )

  logger.info(f"Created {len(uniqueCurrencies)} Currency Types")


def importBooks(driver, chunkSize=1000):
  logger.info("Importing books...")
  with driver.session() as session:
    logger.debug("Loading book data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/book.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)
    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              query = """
                      MERGE (:Book {
                          id: $id,
                          title: $title,
                          publisher: $publisher,
                          publishDate: COALESCE($publishDate, -1),
                          language: $language,
                          isbn13: $isbn13,
                          subtitle: COALESCE($subtitle, ''),
                          isbn10: COALESCE($isbn10, ''),
                          description: COALESCE($description, ''),
                          pageCount: COALESCE($pageCount, -1),
                          averageRating: COALESCE($averageRating, -1),
                          ratingsCount: COALESCE($ratingsCount, 0)
                      })
                      """
              properties = {
                "id": int(row["b_id"]),
                "title": row["b_title"],
                "publisher": row["b_publisher"],
                "publishDate": row["b_publish_date"]
                if pd.notna(row["b_publish_date"])
                else None,
                "language": row["b_language"],
                "isbn13": int(row["b_isbn13"]),
                "subtitle": row["b_subtitle"] if pd.notna(row["b_subtitle"]) else None,
                "isbn10": row["b_isbn10"] if pd.notna(row["b_isbn10"]) else None,
                "description": row["b_description"]
                if pd.notna(row["b_description"])
                else None,
                "pageCount": int(row["b_page_count"])
                if row["b_page_count"] > 0
                else None,
                "averageRating": float(row["b_average_rating"])
                if row["b_average_rating"] > 0
                else None,
                "ratingsCount": int(row["b_rating_count"])
                if row["b_rating_count"] > 0
                else None,
              }
              tx.run(query, properties)

            except Exception as row_error:
              tx.rollback()
              logger.error(
                f"Failed to execute with: {{Index={index}, id={row['b_id']}, b_title={row['b_title']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} books processed"
            )

      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Book import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(f"A total of {totalFailed} books failed to import")


def importPhysicalBooks(driver, chunkSize=1000):
  logger.info("Importing Physical Books...")
  with driver.session() as session:
    logger.debug("Loading physical book data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/physical_book.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MATCH (b:Book {id: $b_id})
                SET b :PhysicalBook
                SET b.coverType = $pb_cover_type, 
                    b.length = $pb_length, 
                    b.width = $pb_width, 
                    b.depth = $pb_depth, 
                    b.weight = $pb_weight
                """,
                b_id=int(row["b_id"]),
                pb_cover_type=row["pb_cover_type"],
                pb_length=float(row["pb_length"]),
                pb_width=float(row["pb_width"]),
                pb_depth=float(row["pb_depth"]),
                pb_weight=float(row["pb_weight"]),
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to execute with: {{Index={index}, b_id={row['b_id']}, pb_cover_type={row['pb_cover_type']}, pb_length={row['pb_length']}, pb_width={row['pb_width']}, pb_depth={row['pb_depth']}, pb_weight={row['pb_weight']}, }} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} physical books processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Physical Book import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(f"A total of {totalFailed} physical books failed to import")


def importEBooks(driver, chunkSize=1000):
  logger.info("Importing EBooks...")
  with driver.session() as session:
    logger.debug("Loading EBook data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/ebook.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MATCH (b:Book {id: $b_id})
                SET b :EBook
                SET b.viewability = $eb_viewability, 
                    b.webReaderLink = $eb_web_reader_link
                """,
                b_id=int(row["b_id"]),
                eb_viewability=row["eb_viewability"],
                eb_web_reader_link=row["eb_web_reader_link"],
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to execute with: {{Index={index}, b_id={row['b_id']}, eb_viewability={row['eb_viewability']}, eb_web_reader_link={row['eb_web_reader_link']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} EBooks processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"EBook import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(f"A total of {totalFailed} EBooks failed to import")


def importAuthorBookRelation(driver, chunkSize=1000):
  logger.info("Mapping authors to books...")
  with driver.session() as session:
    logger.debug("Loading author-book data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/book_author.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MATCH (b:Book {id: $b_id}), (a:Author {id: $a_id})
                MERGE (a)-[:AUTHORED]->(b)
                """,
                b_id=int(row["b_id"]),
                a_id=int(row["a_id"]),
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to create relation: {{Index={index}, b_id={row['b_id']}, a_id={row['a_id']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} authors-book relations processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Author-Book import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(f"A total of {totalFailed} authors-book relations failed to import")


def importBookCategoryRelation(driver, chunkSize=1000):
  logger.info("Mapping categories to books...")
  with driver.session() as session:
    logger.debug("Loading category-book data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/book_category.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MATCH (b:Book {id: $b_id}), (c:Category {id: $c_id})
                MERGE (b)-[:IN_CATEGORY]->(c)
                """,
                b_id=int(row["b_id"]),
                c_id=int(row["c_id"]),
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to create relation: {{Index={index}, b_id={row['b_id']}, c_id={row['c_id']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} category-book relations processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Category-Book import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(f"A total of {totalFailed} category-book relations failed to import")


def importPrices(driver, chunkSize=1000):
  logger.info("Creating and mapping prices to books...")
  with driver.session() as session:
    logger.debug("Loading price data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/price.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MERGE (p:Price {amount: $p_price})
                WITH p
                MATCH (b:Book {id: $b_id}), (ct:CurrencyType {name: $p_currency})
                MERGE (b)-[:COSTS]->(p)
                MERGE (p)-[:IN_CURRENCY]->(ct)
                """,
                b_id=int(row["b_id"]),
                p_price=float(row["p_price"]),
                p_currency=row["p_currency"],
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to create relation: {{Index={index}, p_id={row['p_id']}, p_price={row['p_price']}, p_currency={row['p_currency']}, b_id={row['b_id']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} prices and their relations processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Price import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(
        f"A total of {totalFailed} prices and their relations failed to import"
      )


def importAwards(driver, chunkSize=1000):
  logger.info("Creating and mapping awards to books...")
  with driver.session() as session:
    logger.debug("Loading award data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/award.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MATCH (b:Book {id: $b_id})
                MERGE (aw:Award {id: $aw_id, name: $aw_name, year: $aw_year, level: $aw_level})
                WITH b, aw
                MERGE (b)-[:WON]->(aw)
                """,
                b_id=int(row["b_id"]),
                aw_id=int(row["aw_id"]),
                aw_name=row["aw_name"],
                aw_year=int(row["aw_year"]),
                aw_level=row["aw_level"],
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to create relation: {{Index={index}, aw_id={row['aw_id']}, aw_name={row['aw_name']}, aw_year={row['aw_year']}, aw_level={row['aw_level']}, b_id={row['b_id']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} awards and their relations processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Award import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(
        f"A total of {totalFailed} awards and their relations failed to import"
      )


def importKeywords(driver, chunkSize=1000):
  logger.info("Creating and mapping keywords to books...")
  with driver.session() as session:
    logger.debug("Loading keyword data from CSV...")
    dumpPath = f"{DATA_DUMP_PATH}/keywords.csv"
    csvReader = pd.read_csv(dumpPath, chunksize=chunkSize)

    totalRows = pd.read_csv(dumpPath).shape[0]
    currProcessed = 0
    totalFailed = 0

    for chunk in csvReader:
      try:
        with session.begin_transaction() as tx:
          for index, row in chunk.iterrows():
            try:
              tx.run(
                """
                MATCH (b:Book {id: $b_id})
                MERGE (k:Keyword {name: $k_name})
                ON CREATE SET k.id = $k_id
                WITH b, k
                MERGE (b)-[:HAS_KEYWORD]->(k)
                """,
                b_id=int(row["b_id"]),
                k_id=int(row["k_id"]),
                k_name=row["k_name"],
              )
            except Exception as row_error:
              tx.rollback()

              logger.error(
                f"Failed to create relation: {{Index={index}, k_id={row['k_id']}, k_name={row['k_name']}, b_id={row['b_id']}}} Error: {str(row_error)}"
              )
              totalFailed += len(chunk)
              break
          else:
            # Only commit if no errors occurred in the chunk
            tx.commit()
            currProcessed += len(chunk)
            logger.debug(
              f"Transaction completed: {currProcessed}/{totalRows} keywords and their relations processed"
            )
      except Exception as chunk_error:
        logger.error(f"Error processing chunk: {str(chunk_error)}")

    logger.info(f"Keyword import completed: {currProcessed}/{totalRows}")
    if totalFailed > 0:
      logger.error(
        f"A total of {totalFailed} keywords and their relations failed to import"
      )


if __name__ == "__main__":
  logger.setLevel(logging.DEBUG)
  CHUNCK_SIZE = 1000

  try:
    with GraphDatabase.driver(NEO4J_CONFIG["URI"], auth=NEO4J_CONFIG["auth"]) as driver:
      logger.debug("Verifying Neo4j connectivity...")
      driver.verify_connectivity()

      logger.info("Creating database constraints...")
      execute_cypher_query(driver, "constraints.cypher")

      importAuthors(driver, CHUNCK_SIZE)
      importCategories(driver, CHUNCK_SIZE)
      createCurrencyTypes(driver)
      importBooks(driver, CHUNCK_SIZE)
      importPhysicalBooks(driver, CHUNCK_SIZE)
      importEBooks(driver, CHUNCK_SIZE)
      importAuthorBookRelation(driver, CHUNCK_SIZE)
      importBookCategoryRelation(driver, CHUNCK_SIZE)
      importPrices(driver, CHUNCK_SIZE)
      importAwards(driver, CHUNCK_SIZE)
      importKeywords(driver, CHUNCK_SIZE)
      logger.info("Data import completed successfully")

      logger.info("Creating database indexes...")
      execute_cypher_query(driver, "indexes.cypher")
  except Exception as e:
    logger.error(f"Error during import: {str(e)}")
    exit(1)
