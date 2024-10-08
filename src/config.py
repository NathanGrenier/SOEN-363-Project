import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
  "host": os.getenv("POSTGRES_HOST"),
  "port": 5432,
  "database": os.getenv("POSTGRES_DB"),
  "user": os.getenv("POSTGRES_USER"),
  "password": os.getenv("POSTGRES_PASSWORD"),
}
