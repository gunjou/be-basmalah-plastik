from flask import logging, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .query.q_units import *

units_ns = Namespace("units", description="Units related endpoints")

unit_model = units_ns.model("Unit", {
    "nama": fields.String(required=True, description="Nama satuan produk")
})

@units_ns.route('/')
class UnitListResource(Resource):
    @jwt_required()
    def get(self):
        try:
            data = get_all_units()
            if not data:
                return {'status': "No units found"}, 404
            return data, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500

    @jwt_required()
    @units_ns.expect(unit_model)
    def post(self):
        payload = request.get_json()
        nama = payload.get("nama")

        if not nama:
            return {"status": "Nama satuan tidak boleh kosong"}, 400

        try:
            new_unit = insert_unit(nama)
            if not new_unit:
                return {"status": "Gagal menambahkan satuan"}, 500
            return {"data": new_unit, "status": "Satuan berhasil ditambahkan"}, 201
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

@units_ns.route('/<int:id>')
class UnitDetailResource(Resource):
    @jwt_required()
    def get(self, id):
        try:
            unit = get_unit_by_id(id)
            if not unit:
                return {"status": "Satuan tidak ditemukan"}, 404
            return {"data": unit, "status": "success"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

    @jwt_required()
    @units_ns.expect(unit_model)
    def put(self, id):
        payload = request.get_json()
        nama = payload.get("nama")

        if not nama:
            return {"status": "Nama satuan tidak boleh kosong"}, 400

        try:
            updated = update_unit(id, nama)
            if not updated:
                return {"status": "Satuan tidak ditemukan"}, 404
            return {"status": "Satuan berhasil diupdate"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

    @jwt_required()
    def delete(self, id):
        try:
            deleted = delete_unit(id)
            if not deleted:
                return {"status": "Satuan tidak ditemukan"}, 404
            return {"status": "Satuan berhasil dihapus"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500
