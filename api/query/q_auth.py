from flask_jwt_extended import create_access_token
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..utils.config import get_connection


connection = get_connection().connect()

def login_user(username, password):
    try:
        if username == 'admin':
            result = connection.execute(
                    text("""
                        SELECT * 
                        FROM users
                        WHERE username = :username 
                        AND password_hash = :password;
                    """),
                    {"username": username, "password": password}
                ).mappings().fetchone()
        
            access_token = create_access_token(identity=str(result['id']))
            return {
                'access_token': access_token,
                'message': 'login success',
                'id': result['id'],
                'role': result['role'],
                'nama': 'admin'
            }
        
        else:
            result = connection.execute(
                    text("""
                        SELECT u.id, u.username, u.role, l.nama 
                        FROM users u 
                        INNER JOIN locations l ON u.lokasi_id = l.id 
                        WHERE u.username = :username 
                        AND u.password_hash = :password;
                    """),
                    {"username": username, "password": password}
                ).mappings().fetchone()
        
            access_token = create_access_token(identity=str(result['id']))
            return {
                'access_token': access_token,
                'message': 'login success',
                'id': result['id'],
                'role': result['role'],
                'nama': result['nama']
            }
        
    except SQLAlchemyError as e:
        print(f"Error occurred: {str(e)}")  # Log kesalahan
        return {'msg': 'Internal server error'}