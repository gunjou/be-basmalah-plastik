from flask import logging, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .query.q_auth import login_user
from .blacklist_store import add_to_blacklist


auth_ns = Namespace("auth", description="Auth related endpoints")

login_model = auth_ns.model("Login", {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
})

@auth_ns.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        return {'status': 'Token masih aktif'}, 200

@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        auth = request.get_json()
        username = auth.get('username')
        password = auth.get('password')

        # validate input
        if not username or not password:
            return {'status': "username dan password tidak boleh kosong"}, 400  # Bad Request

        try:
            get_jwt_response = login_user(username, password)
            if get_jwt_response is None:
                return {'status': "Invalid username or password"}, 401  # Unauthorized

            return get_jwt_response, 200  # OK
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500  # Internal Server Error
    
@auth_ns.route('/logout')
class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        add_to_blacklist(jti)
        return {'status': "Logout berhasil, token di-blacklist"}, 200