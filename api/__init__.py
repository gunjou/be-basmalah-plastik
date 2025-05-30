from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from .utils.blacklist_store import is_token_revoked
from .auth import auth_ns
from .user import user_ns
from .lokasi import lokasi_ns
from .produk import produk_ns
from .stok import stok_ns
from .mutasi_stok import mutasi_stok_ns
from .pelanggan import pelanggan_ns
from .transaksi import transaksi_ns
from .hutang import hutang_ns
from .laporan import laporan_ns

api = Flask(__name__)
CORS(api)

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
restx_api.add_namespace(user_ns, path="/user")
restx_api.add_namespace(lokasi_ns, path="/lokasi")
restx_api.add_namespace(produk_ns, path="/produk")
restx_api.add_namespace(stok_ns, path="/stok")
restx_api.add_namespace(mutasi_stok_ns, path="/mutasi-stok")
restx_api.add_namespace(pelanggan_ns, path="/pelanggan")
restx_api.add_namespace(transaksi_ns, path="/transaksi")
restx_api.add_namespace(hutang_ns, path="/hutang")
restx_api.add_namespace(laporan_ns, path="/laporan")