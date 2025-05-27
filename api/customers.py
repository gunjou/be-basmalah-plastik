from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
import logging
from .query.q_customers import add_customer, get_customers, check_duplicate_customer

customers_ns = Namespace("customers", description="API pelanggan")

customer_model = customers_ns.model("Customer", {
    "nama": fields.String(required=True),
    "lokasi_id": fields.Integer(required=True),
    "alamat": fields.String(required=False),
    "telepon": fields.String(required=False)
})

@customers_ns.route('')
class CustomerList(Resource):
    @jwt_required()
    def get(self):
        lokasi_id = request.args.get("lokasi_id", type=int)
        try:
            customers = get_customers(lokasi_id)
            return {"status": "success", "data": customers}, 200
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500

    @jwt_required()
    @customers_ns.expect(customer_model)
    def post(self):
        data = request.get_json()
        try:
            # Cek duplikat
            if check_duplicate_customer(data["nama"], data["lokasi_id"]):
                return {"status": "Pelanggan dengan nama dan lokasi tersebut sudah ada"}, 400

            result = add_customer(data)
            return {"status": "Pelanggan berhasil ditambahkan", "data": result}, 201
        except Exception as e:
            logging.error(str(e))
            return {"status": "Terjadi kesalahan server"}, 500
