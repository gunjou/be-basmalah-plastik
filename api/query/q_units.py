from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..config import get_connection

connection = get_connection().connect()

def get_all_units():
    try:
        result = connection.execute(
            text("SELECT * FROM units")
        ).mappings().fetchall()
        return [dict(row) for row in result]
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def insert_unit(nama):
    try:
        result = connection.execute(
            text("INSERT INTO units (nama) VALUES (:nama) RETURNING id, nama"),
            {"nama": nama}
        ).mappings().fetchone()
        connection.commit()
        return dict(result)
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def get_unit_by_id(unit_id):
    try:
        result = connection.execute(
            text("SELECT * FROM units WHERE id = :id"),
            {"id": unit_id}
        ).mappings().fetchone()
        return dict(result) if result else None
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def update_unit(unit_id, nama):
    try:
        result = connection.execute(
            text("UPDATE units SET nama = :nama WHERE id = :id RETURNING id"),
            {"id": unit_id, "nama": nama}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def delete_unit(unit_id):
    try:
        result = connection.execute(
            text("DELETE FROM units WHERE id = :id RETURNING id"),
            {"id": unit_id}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
