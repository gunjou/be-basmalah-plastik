from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from .query.q_transactions import *
from .query.q_debts import *

transactions_ns = Namespace("transactions", description="Transaction related endpoints")

item_model = transactions_ns.model("TransactionItem", {
    "product_id": fields.Integer(required=True),
    "jumlah": fields.Float(required=True),
    "harga": fields.Float(required=True),
    "subtotal": fields.Float(required=True)
})

transaction_model = transactions_ns.model("Transaction", {
    "tanggal": fields.String(required=False),
    "lokasi_id": fields.Integer(required=True),
    "kasir_id": fields.Integer(required=True),
    "pelanggan_id": fields.Integer(required=False),
    "total": fields.Float(required=True),
    "tunai": fields.Float(required=True),
    "kembalian": fields.Float(required=True),
    "items": fields.List(fields.Nested(item_model), required=True)
})

@transactions_ns.route('/')
class TransactionList(Resource):
    @jwt_required()
    @transactions_ns.expect(transaction_model)
    def post(self):
        data = request.get_json()
        try:
            if data['tunai'] < data['total'] and not data.get('pelanggan_id'):
                return {"status": "Pelanggan wajib diisi jika pembayaran kurang dari total."}, 400

            transaction = add_transaction(data)

            if data['tunai'] < data['total']:
                hutang = data['total'] - data['tunai']
                add_debt({
                    "transaction_id": transaction['id'],
                    "pelanggan_id": data['pelanggan_id'],
                    "lokasi_id": data['lokasi_id'],
                    "jumlah_hutang": hutang
                })

            return {"status": "Transaksi berhasil disimpan", "data": transaction}, 201
        except SQLAlchemyError as e:
            return {"status": "Terjadi kesalahan di server", "error": str(e)}, 500

@transactions_ns.route('/<int:id>')
class TransactionDetail(Resource):
    @jwt_required()
    def get(self, id):
        try:
            transaction = get_transaction_detail(id)
            if not transaction:
                return {"status": "Transaksi tidak ditemukan"}, 404
            return {"data": transaction}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

@transactions_ns.route('/print_invoice/<int:id>')
class TransactionInvoice(Resource):
    @jwt_required()
    def get(self, id):
        try:
            invoice_data = get_invoice_data(id)
            if not invoice_data:
                return {"status": "Data invoice tidak ditemukan"}, 404
            return {"data": invoice_data}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500
