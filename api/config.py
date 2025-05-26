import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

# load .env
load_dotenv()

# === Konfigurasi Database === #
def get_connection():
    # server = 'localhost:5432' # localhost
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")

    return create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}')
