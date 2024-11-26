import logging

from config import NEO4J_CONFIG, logger
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


# def importActors(driver):
#   logger.info("Importing actors...")
#   query = """
#     LOAD CSV WITH HEADERS FROM 'file:///dump/actor.csv' AS row
#     MERGE (a:Actor {id: toInteger(row.a_id), firstName: split(trim(row.a_name), ' ')[0], lastName: split(trim(row.a_name), ' ')[-1]})
#     RETURN count(a) as actor_count
#     """
#   result, summary, _ = driver.execute_query(query)
#   logger.debug(f"Imported {result[0]['actor_count']} actors")


if __name__ == "__main__":
  logger.setLevel(logging.DEBUG)

  try:
    with GraphDatabase.driver(NEO4J_CONFIG["URI"], auth=NEO4J_CONFIG["auth"]) as driver:
      logger.debug("Verifying Neo4j connectivity...")
      driver.verify_connectivity()

      logger.info("Creating database constraints...")
      execute_cypher_query(driver, "constraints.cypher")

      #   importActors(driver)
      #   importCountry(driver)
      #   importMovies(driver)
      #   importMovieActorRelation(driver)
      #   importMovieCountryRelation(driver)
      #   importKeyword(driver)
      logger.info("Data import completed successfully")

      logger.info("Creating database indexes...")
      execute_cypher_query(driver, "indexes.cypher")
  except Exception as e:
    logger.error(f"Error during import: {str(e)}")
    exit(1)
