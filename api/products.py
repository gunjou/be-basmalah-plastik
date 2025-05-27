from flask import logging, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .query.q_products import *

products_ns = Namespace("products", description="Products related endpoints")

product_model = products_ns.model("Product", {
    "nama": fields.String(required=True, description="Nama produk"),
    "barcode": fields.String(required=False, description="Kode barcode produk"),
    "id_kategori": fields.Integer(required=True, description="ID kategori produk"),
    "id_satuan": fields.Integer(required=True, description="ID satuan produk"),
    "harga_beli": fields.Float(required=True, description="Harga beli produk"),
    "harga_jual": fields.Float(required=True, description="Harga jual produk")
})

@products_ns.route('/')
class ProductListResource(Resource):
    # @jwt_required()
    def get(self):
        try:
            data = get_all_products()
            if not data:
                return {'status': "No products found"}, 404
            return data, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500

    # @jwt_required()
    @products_ns.expect(product_model)
    def post(self):
        payload = request.get_json()
        try:
            new_product = insert_product(payload)
            if not new_product:
                return {"status": "Gagal menambahkan produk"}, 500
            return {"data": new_product, "status": "Produk berhasil ditambahkan"}, 201
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

@products_ns.route('/<int:id>')
class ProductDetailResource(Resource):
    # @jwt_required()
    def get(self, id):
        try:
            product = get_product_by_id(id)
            if not product:
                return {"status": "Produk tidak ditemukan"}, 404
            return {"data": product, "status": "success"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

    # @jwt_required()
    @products_ns.expect(product_model)
    def put(self, id):
        payload = request.get_json()
        try:
            updated = update_product(id, payload)
            if not updated:
                return {"status": "Produk tidak ditemukan"}, 404
            return {"status": "Produk berhasil diupdate"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500

    # @jwt_required()
    def delete(self, id):
        try:
            deleted = delete_product(id)
            if not deleted:
                return {"status": "Produk tidak ditemukan"}, 404
            return {"status": "Produk berhasil dihapus"}, 200
        except SQLAlchemyError:
            return {"status": "Terjadi kesalahan di server"}, 500
