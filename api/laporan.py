from flask import logging, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from .query.q_laporan import *

laporan_ns = Namespace("laporan", description="Laporan related endpoints")

laporan_model = laporan_ns.model("Laporan", {
    "nama_laporan": fields.String(required=True, description="Nama Laporan"),
    "kontak": fields.String(required=False, description="Kontak (hp)"),
})


@laporan_ns.route('/transaksi')
class LaporanListResource(Resource):
    # @jwt_required()
    def get(self):
        try:
            result = get_all_laporan_transaksi()
            if not result:
                return {'status': 'error', 'message': 'Tidak ada laporan yang ditemukan'}, 404
            return {'data': result}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500
        

@laporan_ns.route('/penjualan-item')
class LaporanPenjualanItemResource(Resource):
    # @jwt_required()
    @laporan_ns.param("id_produk", "Filter berdasarkan ID produk", type="integer")
    @laporan_ns.param("id_lokasi", "Filter berdasarkan ID lokasi", type="integer")
    def get(self):
        """
        Laporan penjualan item per produk yang sudah diakumulasi.
        Termasuk total qty, subtotal, modal, dan keuntungan.
        Bisa difilter berdasarkan id_produk dan/atau id_lokasi.
        """
        id_produk = request.args.get("id_produk", type=int)
        id_lokasi = request.args.get("id_lokasi", type=int)
        try:
            result = get_laporan_penjualan_item_grouped(id_produk, id_lokasi)
            if not result:
                return {'status': 'error', 'message': 'Tidak ada data penjualan item ditemukan'}, 404
            return {'data': result}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500


@laporan_ns.route('/stok')
class LaporanStokResource(Resource):
    # @jwt_required()
    @laporan_ns.param("id_produk", "Filter berdasarkan ID produk", type="integer")
    @laporan_ns.param("id_lokasi", "Filter berdasarkan ID lokasi", type="integer")
    def get(self):
        """
        Laporan stok per item, termasuk nilai modal dan potensi keuntungan.
        Bisa difilter berdasarkan id_produk dan id_lokasi.
        """
        id_produk = request.args.get("id_produk", type=int)
        id_lokasi = request.args.get("id_lokasi", type=int)

        try:
            result = get_laporan_stok(id_produk=id_produk, id_lokasi=id_lokasi)
            if not result:
                return {'status': 'error', 'message': 'Tidak ada data stok ditemukan'}, 404
            return {'data': result}, 200
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            return {'status': "Internal server error"}, 500
