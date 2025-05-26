from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..config import get_connection


connection = get_connection().connect()

def get_all_categories():
    try:
        result = connection.execute(
                text("""SELECT * FROM categories;""")).mappings().fetchall()
        
        return [dict(row) for row in result]
    
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")  # Log kesalahan
        return {'msg': 'Internal server error'}
    
def insert_category(nama):
    try:
        result = connection.execute(
            text("INSERT INTO categories (nama) VALUES (:nama) RETURNING id, nama"),
            {"nama": nama}
        ).mappings().fetchone()
        return dict(result)
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def get_category_by_id(category_id):
    try:
        result = connection.execute(
            text("SELECT * FROM categories WHERE id = :id"),
            {"id": category_id}
        ).mappings().fetchone()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def update_category(category_id, nama):
    try:
        result = connection.execute(
            text("UPDATE categories SET nama = :nama WHERE id = :id RETURNING id"),
            {"id": category_id, "nama": nama}
        ).fetchone()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None

def delete_category(category_id):
    try:
        result = connection.execute(
            text("DELETE FROM categories WHERE id = :id RETURNING id"),
            {"id": category_id}
        ).fetchone()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None