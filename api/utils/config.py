import os
import pytz
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine


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

    # return create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}')
    # Tambah parameter pool_size, max_overflow, pool_timeout, pool_recycle
    engine = create_engine(
        f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}',
        pool_size=10,          # jumlah koneksi tetap dalam pool
        max_overflow=5,        # jumlah koneksi tambahan saat pool penuh
        pool_timeout=30,       # waktu tunggu saat pool penuh (detik)
        pool_recycle=1800      # recycle koneksi setiap 30 menit agar tidak timeout
    )
    return engine

# === Mencari Timestamp WITA === #
def get_wita():
    wita = pytz.timezone('Asia/Makassar')
    now_wita = datetime.now(wita)
    return now_wita.replace(tzinfo=None)