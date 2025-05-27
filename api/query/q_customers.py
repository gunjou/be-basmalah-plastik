from sqlalchemy import text
from ..config import get_connection

connection = get_connection().connect()

def check_duplicate_customer(nama, lokasi_id):
    query = text("""
        SELECT * FROM customers WHERE nama = :nama AND lokasi_id = :lokasi_id
    """)
    result = connection.execute(query, {"nama": nama, "lokasi_id": lokasi_id}).mappings().fetchone()
    return dict(result) if result else None

def add_customer(data):
    query = text("""
        INSERT INTO customers (nama, lokasi_id, alamat, telepon)
        VALUES (:nama, :lokasi_id, :alamat, :telepon)
        RETURNING *
    """)
    result = connection.execute(query, data).mappings().fetchone()
    connection.commit()
    return dict(result)

def get_customers(lokasi_id=None):
    query = "SELECT * FROM customers WHERE 1=1"
    params = {}
    if lokasi_id:
        query += " AND lokasi_id = :lokasi_id"
        params["lokasi_id"] = lokasi_id
    result = connection.execute(text(query), params).mappings().fetchall()
    return [dict(row) for row in result]
