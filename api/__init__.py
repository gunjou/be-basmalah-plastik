from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from .blacklist_store import is_token_revoked
from .auth import auth_ns
from .categories import categories_ns
from .units import units_ns
from .products import products_ns
from .stocks import stocks_ns
from .transactions import transactions_ns
from .debts import debts_ns
from .customers import customers_ns
from .reports import reports_ns

api = Flask(__name__)
CORS(app=api)

api.config['JWT_SECRET_KEY'] = 'basmalahplastik2025'
api.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=20)  # Atur sesuai kebutuhan
api.config['JWT_BLACKLIST_ENABLED'] = True
api.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# api.register_blueprint(auth_bp, name='auth')

jwt = JWTManager(api)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return is_token_revoked(jti)

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Masukkan token JWT Anda dengan format: **Bearer &lt;JWT&gt;**'
    }
}

# Swagger API instance
restx_api = Api(
        api, 
        version="1.0", 
        title="Basmalah Plastik", 
        description="Dokumentasi API Kasir Basmalah", 
        doc="/documentation",
        authorizations=authorizations,
        security='Bearer Auth'
    )

restx_api.add_namespace(auth_ns, path="/auth")
restx_api.add_namespace(categories_ns, path="/categories")
restx_api.add_namespace(units_ns, path="/units")
restx_api.add_namespace(products_ns, path="/products")
restx_api.add_namespace(stocks_ns, path="/stocks")
restx_api.add_namespace(transactions_ns, path="/transactions")
restx_api.add_namespace(debts_ns, path="/debts")
restx_api.add_namespace(customers_ns, path="/customers")
restx_api.add_namespace(reports_ns, path="/reports")