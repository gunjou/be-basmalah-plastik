from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..utils.config import get_connection

connection = get_connection().connect()

def get_all_lokasi():
    try:
        result = connection.execute(text("""
            SELECT id_lokasi, nama_lokasi, tipe
            FROM lokasi
            WHERE status = 1;   
        """)).mappings().fetchall()
        return [dict(row) for row in result]
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def insert_lokasi(data):
    try:
        result = connection.execute(text("""
            INSERT INTO lokasi (nama_lokasi, tipe, status)
            VALUES (:nama_lokasi, :tipe, 1)
            RETURNING nama_lokasi
        """), data).mappings().fetchone()
        connection.commit()
        return dict(result)
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def get_lokasi_by_id(id_lokasi):
    try:
        result = connection.execute(text("""
            SELECT id_lokasi, nama_lokasi, tipe
            FROM lokasi
            WHERE id_lokasi = :id_lokasi
            AND status = 1;   
        """), {'id_lokasi': id_lokasi}).mappings().fetchone()
        return dict(result) if result else None
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def update_lokasi(id_lokasi, data):
    try:
        result = connection.execute(
            text("""
                UPDATE lokasi SET nama_lokasi = :nama_lokasi, tipe = :tipe, updated_at = CURRENT_TIMESTAMP
                WHERE id_lokasi = :id_lokasi RETURNING nama_lokasi;
                """
                ),
            {**data, "id_lokasi": id_lokasi}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    
def delete_lokasi(id_lokasi):
    try:
        result = connection.execute(
            text("UPDATE lokasi SET status = 0, updated_at = CURRENT_TIMESTAMP WHERE status = 1 AND id_lokasi = :id_lokasi RETURNING nama_lokasi;"),
            {"id_lokasi": id_lokasi}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None