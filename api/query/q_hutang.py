from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..utils.config import get_connection, get_wita

connection = get_connection().connect()
timestamp_wita = get_wita()

def get_all_hutang():
    try:
        result = connection.execute(text("""
            SELECT id_hutang, id_transaksi, id_pelanggan, sisa_hutang, status_hutang
            FROM hutang
            WHERE status = 1
            AND status_hutang = 'belum lunas';   
        """)).mappings().fetchall()
        return [dict(row) for row in result]
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def insert_hutang(data):
    try:
        result = connection.execute(text("""
            INSERT INTO hutang (id_transaksi, id_pelanggan, sisa_hutang, status_hutang, status, created_at, updated_at)
            VALUES (:id_transaksi, :id_pelanggan, :sisa_hutang, :status_hutang, 1, :timestamp_wita, :timestamp_wita)
            RETURNING sisa_hutang, status_hutang
        """), {**data, "timestamp_wita": timestamp_wita}).mappings().fetchone()
        connection.commit()
        return dict(result)
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def get_hutang_by_id(id_hutang):
    try:
        result = connection.execute(text("""
            SELECT id_hutang, id_transaksi, id_pelanggan, sisa_hutang, status_hutang
            FROM hutang
            WHERE id_hutang = :id_hutang
            AND status = 1
            AND status_hutang = 'belum lunas';   
        """), {'id_hutang': id_hutang}).mappings().fetchone()
        return dict(result) if result else None
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def update_hutang(id_hutang, data):
    try:
        result = connection.execute(
            text("""
                UPDATE hutang SET sisa_hutang = :sisa_hutang, status_hutang = :status_hutang, updated_at = :timestamp_wita
                WHERE id_hutang = :id_hutang AND status_hutang = 'belum lunas' RETURNING sisa_hutang, status_hutang;
                """
                ),
            {**data, "id_hutang": id_hutang, "timestamp_wita": timestamp_wita}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    
def delete_hutang(id_hutang):
    try:
        result = connection.execute(
            text("""UPDATE hutang SET status = 0, updated_at = :timestamp_wita 
                 WHERE status = 1 AND id_hutang = :id_hutang
                 RETURNING id_hutang;"""),
            {"id_hutang": id_hutang, "timestamp_wita": timestamp_wita}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    
def count_total_hutang(id_pelanggan=None):
    try:
        query = """
            SELECT COALESCE(SUM(sisa_hutang), 0) AS total_hutang
            FROM hutang
            WHERE status = 1 AND status_hutang = 'belum lunas'
        """
        params = {}

        if id_pelanggan:
            query += " AND id_pelanggan = :id_pelanggan"
            params["id_pelanggan"] = id_pelanggan

        result = connection.execute(text(query), params).scalar()
        return result
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return 0
