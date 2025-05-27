# query/q_products.py
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from ..config import get_connection

connection = get_connection().connect()

def get_product_by_barcode(barcode):
    query = text("SELECT * FROM products WHERE barcode = :barcode")
    result = connection.execute(query, {"barcode": barcode}).mappings().fetchone()
    return dict(result) if result else None

def add_product(data):
    query = text("""
        INSERT INTO products (nama, barcode, id_kategori, id_satuan, harga_beli, harga_jual)
        VALUES (:nama, :barcode, :id_kategori, :id_satuan, :harga_beli, :harga_jual)
        RETURNING *
    """)
    result = connection.execute(query, data).mappings().fetchone()
    return dict(result)

def convert_decimal_to_float(data):
    if isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in data.items()}
    return data

def get_all_products():
    try:
        result = connection.execute(text("""
            SELECT 
                p.*, 
                c.nama AS nama_kategori,
                u.nama AS nama_satuan
            FROM products p
            LEFT JOIN categories c ON p.id_kategori = c.id
            LEFT JOIN units u ON p.id_satuan = u.id
        """)).mappings().fetchall()
        return convert_decimal_to_float([dict(row) for row in result])
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return []

def insert_product(data):
    try:
        result = connection.execute(text("""
            INSERT INTO products (nama, barcode, id_kategori, id_satuan, harga_beli, harga_jual)
            VALUES (:nama, :barcode, :id_kategori, :id_satuan, :harga_beli, :harga_jual)
            RETURNING id, nama
        """), data).mappings().fetchone()
        connection.commit()
        return dict(result)
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return None

def get_product_by_id(product_id):
    try:
        result = connection.execute(text("""
            SELECT 
                p.*, 
                c.nama AS nama_kategori,
                u.nama AS nama_satuan
            FROM products p
            LEFT JOIN categories c ON p.id_kategori = c.id
            LEFT JOIN units u ON p.id_satuan = u.id
            WHERE p.id = :id
        """), {"id": product_id}).mappings().fetchone()
        return convert_decimal_to_float(dict(result) if result else None)
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def update_product(product_id, data):
    try:
        result = connection.execute(text("""
            UPDATE products 
            SET nama = :nama, barcode = :barcode, id_kategori = :id_kategori,
                id_satuan = :id_satuan, harga_beli = :harga_beli, harga_jual = :harga_jual
            WHERE id = :id RETURNING id
        """), {**data, "id": product_id}).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def delete_product(product_id):
    try:
        result = connection.execute(
            text("DELETE FROM products WHERE id = :id RETURNING id"),
            {"id": product_id}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
