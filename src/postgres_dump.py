import logging
import os

import psycopg

from config import (
  DATA_DUMP_PATH,
  POSTGRES_CONFIG,
  logger,
)


def export_tables_to_csv(conn, outputDir, tables):
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)

  with conn.cursor() as cur:
    for table in tables:
      tableName = table[0]
      isView = table[1] == "VIEW"
      outputFile = os.path.join(outputDir, f"{tableName}.csv")

      sql = (
        f"COPY (SELECT * FROM {tableName}) TO STDOUT WITH (FORMAT CSV, HEADER)"
        if isView
        else f"COPY {tableName} TO STDOUT WITH (FORMAT CSV, HEADER)"
      )

      with cur.copy(sql) as copy:
        with open(outputFile, "wb") as f:
          while data := copy.read():
            f.write(data)
      logger.debug(
        f"Exported {'view' if isView else 'table'} '{tableName}' to {outputFile}"
      )


def get_public_tables(conn):
  with conn.cursor() as cur:
    cur.execute(
      """
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
    )
    return cur.fetchall()


if __name__ == "__main__":
  logger.setLevel(logging.DEBUG)

  try:
    with psycopg.connect(**POSTGRES_CONFIG) as conn:
      tables = get_public_tables(conn)
      if not tables:
        logger.warning("No tables found in public schema")
        exit(0)

      logger.info(f"Found {len(tables)} tables to export")
      export_tables_to_csv(conn, DATA_DUMP_PATH, tables)
      logger.info("Export completed successfully")

  except psycopg.Error as e:
    logger.error(f"Database error occurred: {str(e)}")
    exit(1)
  except Exception as e:
    logger.error(f"Unexpected error occurred: {str(e)}")
    exit(1)
