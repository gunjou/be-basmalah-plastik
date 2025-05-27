from flask import logging, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .query.q_categories import *


categories_ns = Namespace("categories", description="Categories related endpoints")

category_model = categories_ns.model("Category", {
    "nama": fields.String(required=True, description="Nama kategori produk")
})
        
@categories_ns.route('/')
class CategoryCreate(Resource):
    # @jwt_required()
    def get(self):
        try:
            data = get_all_categories()
            if not data:
                return {'status': "No categories found"}, 404

            return data, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500
        
    # @jwt_required()
    @categories_ns.expect(category_model)
    def post(self):
        payload = request.get_json()
        nama = payload.get("nama")

        if not nama:
            return {"status": "Nama kategori tidak boleh kosong"}, 400

        try:
            new_category = insert_category(nama)
            if not new_category:
                return {"status": "Gagal menambahkan kategori"}, 500
            return {"data": new_category, "status": "Kategori berhasil ditambahkan"}, 201
        except SQLAlchemyError as e:
            return {"status": "Terjadi kesalahan di server"}, 500
        

@categories_ns.route('/<int:id>')
class CategoryDetailResource(Resource):
    # @jwt_required()
    def get(self, id):
        try:
            category = get_category_by_id(id)
            if not category:
                return {"status": "Kategori tidak ditemukan"}, 404
            return {"data": category, "status": "success"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500
        
    # @jwt_required()
    @categories_ns.expect(category_model)
    def put(self, id):
        payload = request.get_json()
        nama = payload.get("nama")

        if not nama:
            return {"status": "Nama kategori tidak boleh kosong"}, 400

        try:
            updated = update_category(id, nama)
            if not updated:
                return {"status": "Kategori tidak ditemukan"}, 404
            return {"status": "Kategori berhasil diupdate"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

    # @jwt_required()
    def delete(self, id):
        try:
            deleted = delete_category(id)
            if not deleted:
                return {"status": "Kategori tidak ditemukan"}, 404
            return {"status": "Kategori berhasil dihapus"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500