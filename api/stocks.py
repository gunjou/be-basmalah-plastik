from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
import logging

from .query.q_stocks import *

stocks_ns = Namespace("stocks", description="Stock related endpoints")

stock_input_model = stocks_ns.model("StockInput", {
    "nama": fields.String(required=True),
    "barcode": fields.String(required=True),
    "jumlah": fields.Integer(required=True),
    "harga_beli": fields.Float(required=True),
    "harga_jual": fields.Float(required=True),
    "id_kategori": fields.Integer(required=True),
    "id_satuan": fields.Integer(required=True),
    "location_id": fields.Integer(required=True),
    "keterangan": fields.String(required=False)
})

transfer_model = stocks_ns.model("StockTransfer", {
    "product_id": fields.Integer(required=True),
    "from_location": fields.Integer(required=True),
    "to_location": fields.Integer(required=True),
    "jumlah": fields.Float(required=True),
    "keterangan": fields.String(required=False)
})


@stocks_ns.route('/')
class StockList(Resource):
    # @jwt_required()
    def get(self):
        try:
            location_id = request.args.get('location_id')
            product_id = request.args.get('product_id')
            stocks = get_stocks(product_id, location_id)
            return {"data": stocks}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error fetching stock list: {str(e)}")
            return {"status": "Terjadi kesalahan di server"}, 500


@stocks_ns.route('/<int:product_id>/<int:location_id>/')
class StockDetail(Resource):
    # @jwt_required()
    def get(self, product_id, location_id):
        try:
            stock = get_stock_detail(product_id, location_id)
            if not stock:
                return {"status": "Data stok tidak ditemukan"}, 404
            return {"data": stock}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error fetching stock detail: {str(e)}")
            return {"status": "Terjadi kesalahan di server"}, 500

# stocks.py
@stocks_ns.route('/in')
class StockIn(Resource):
    # @jwt_required()
    @stocks_ns.expect(stock_input_model)
    def post(self):
        data = request.get_json()
        try:
            result = add_stock(data)
            return {"status": "Stok berhasil ditambahkan", "data": result}, 201
        except SQLAlchemyError as e:
            logging.error(f"Error in stock-in: {str(e)}")
            return {"status": "Terjadi kesalahan di server"}, 500


@stocks_ns.route('/out')
class StockOut(Resource):
    # @jwt_required()
    @stocks_ns.expect(stock_input_model)
    def post(self):
        data = request.get_json()
        try:
            result = reduce_stock(data)
            if result is None:
                return {"status": "Stok tidak mencukupi atau tidak ditemukan"}, 400
            return {"status": "Stok berhasil dikurangi", "data": result}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error in stock-out: {str(e)}")
            return {"status": "Terjadi kesalahan di server"}, 500


@stocks_ns.route('/transfer')
class StockTransfer(Resource):
    # @jwt_required()
    @stocks_ns.expect(transfer_model)
    def post(self):
        data = request.get_json()
        try:
            result = transfer_stock(data)
            return {"status": "Transfer stok berhasil", "data": result}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error in stock transfer: {str(e)}")
            return {"status": "Terjadi kesalahan di server"}, 500


@stocks_ns.route('/history')
class StockHistoryResource(Resource):
    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', type=int)
        parser.add_argument('location_id', type=int)
        parser.add_argument('start_date', type=str, help="Format: YYYY-MM-DD")
        parser.add_argument('end_date', type=str, help="Format: YYYY-MM-DD")
        args = parser.parse_args()

        try:
            history = get_stock_history(
                product_id=args.get('product_id'),
                location_id=args.get('location_id'),
                start_date=args.get('start_date'),
                end_date=args.get('end_date')
            )
            if not history:
                return {"status": "Tidak ada riwayat stok ditemukan"}, 404
            return {"data": history, "status": "success"}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error fetching stock history: {str(e)}")
            return {"status": "Terjadi kesalahan di server"}, 500


@stocks_ns.route('/opname')
class StockOpnameResource(Resource):
    # @jwt_required()
    def post(self):
        payload = request.get_json()
        required_fields = ["product_id", "location_id", "jumlah_fisik"]
        if not all(field in payload for field in required_fields):
            return {"status": "Missing required fields"}, 400

        try:
            result = perform_stock_opname(payload)
            if not result:
                return {"status": "Stok tidak ditemukan"}, 404
            return {"status": "Stok disesuaikan", "data": result}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error in stock opname: {str(e)}")
            return {"status": "Terjadi kesalahan"}, 500


@stocks_ns.route('/opname/history')
class StockOpnameLogResource(Resource):
    # @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', type=int)
        parser.add_argument('location_id', type=int)
        args = parser.parse_args()

        try:
            logs = get_opname_logs(args.get("product_id"), args.get("location_id"))
            return {"status": "success", "data": logs}, 200
        except SQLAlchemyError as e:
            logging.error(f"Error fetching opname logs: {str(e)}")
            return {"status": "Terjadi kesalahan saat mengambil data"}, 500
