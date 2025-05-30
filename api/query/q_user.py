from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..utils.config import get_connection, get_wita

connection = get_connection().connect()
timestamp_wita = get_wita()

def get_all_users():
    try:
        result = connection.execute(text("""
            SELECT id_user, id_lokasi, username, password, role
            FROM users
            WHERE status = 1;   
        """)).mappings().fetchall()
        return [dict(row) for row in result]
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def insert_user(data):
    try:
        result = connection.execute(text("""
            INSERT INTO users (id_lokasi, username, password, role, status)
            VALUES (:id_lokasi, :username, :password, :role, 1)
            RETURNING username
        """), data).mappings().fetchone()
        connection.commit()
        return dict(result)
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def get_user_by_id(id_user):
    try:
        result = connection.execute(text("""
            SELECT id_user, id_lokasi, username, password, role
            FROM users
            WHERE id_user = :id_user
            AND status = 1;   
        """), {'id_user': id_user}).mappings().fetchone()
        return dict(result) if result else None
    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def update_user(id_user, data):
    try:
        result = connection.execute(
            text("""
                UPDATE users SET id_lokasi = :id_lokasi, username = :username, password = :password, role = :role, updated_at = :timestamp_wita 
                WHERE id_user = :id_user RETURNING username;
                """
                ),
            {**data, "id_user": id_user, "timestamp_wita": timestamp_wita}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    
def delete_user(id_user):
    try:
        result = connection.execute(
            text("UPDATE users SET status = 0, updated_at = :timestamp_wita WHERE status = 1 AND id_user = :id_user RETURNING username;"),
            {"id_user": id_user, "timestamp_wita": timestamp_wita}
        ).fetchone()
        connection.commit()
        return result
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return None