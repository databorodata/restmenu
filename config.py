from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("POSTGRES_HOST")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_USER = os.environ.get("POSTGRES_USER")
