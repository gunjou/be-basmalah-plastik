from flask import logging, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .query.q_hutang import *

hutang_ns = Namespace("hutang", description="Hutang related endpoints")

hutang_model = hutang_ns.model("Hutang", {
    "id_transaksi": fields.Integer(required=False, description="id transaksi"),
    "id_pelanggan": fields.Integer(required=True, description="id pelanggan"),
    "sisa_hutang": fields.Integer(required=True, description="sisa hutang"),
    "status_hutang": fields.String(required=True, description="status hutang"),
})

@hutang_ns.route('/')
class HutangListResource(Resource):
    # @jwt_required()
    def get(self):
        try:
            result = get_all_hutang()
            if not result:
                return {'status': 'error', 'message': 'Tidak ada hutang yang ditemukan'}, 401
            return result, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500
        
    # @jwt_required()
    @hutang_ns.expect(hutang_model)
    def post(self):
        payload = request.get_json()
        try:
            new_hutang = insert_hutang(payload)
            if not new_hutang:
                return {"status": "Gagal menambahkan hutang"}, 401
            return {"data": new_hutang, "status": f"Hutang {new_hutang['sisa_hutang']} {new_hutang['status_hutang']} berhasil ditambahkan"}, 201
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500


@hutang_ns.route('/<int:id_hutang>')
class HutangDetailResource(Resource):
    # @jwt_required()
    def get(self, id_hutang):
        try:
            hutang = get_hutang_by_id(id_hutang)
            if not hutang:
                return {'status': 'error', 'message': 'Tidak ada hutang yang ditemukan'}, 401
            return {'data': hutang}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500
        
    # @jwt_required()
    @hutang_ns.expect(hutang_model)
    def put(self, id_hutang):
        payload = request.get_json()
        try:
            updated = update_hutang(id_hutang, payload)
            if not updated:
                return {'status': 'error', "message": "Hutang tidak ditemukan"}, 401
            return {"status": f"Hutang {updated[0]} {updated[1]} berhasil diupdate"}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500  
        
    # @jwt_required()
    def delete(self, id_hutang):
        try:
            deleted = delete_hutang(id_hutang)
            if not deleted:
                return {'status': 'error', "message": "Hutang tidak ditemukan"}, 401
            return {"status": f"Hutang {deleted[0]} berhasil dihapus"}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500 
        

@hutang_ns.route('/total')
class HutangCountResource(Resource):
    # @jwt_required()
    @hutang_ns.param("id_pelanggan", "Filter berdasarkan ID pelanggan", type="integer")
    def get(self):
        """
        total hutang dengan optional filter
        """
        id_pelanggan = request.args.get("id_pelanggan", type=int)
        try:
            total = count_total_hutang(id_pelanggan)
            if total == 0:
                return {'status': 'error', 'message': 'Tidak ada hutang yang ditemukan'}, 404
            return {'total_hutang': total}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500
