from datetime import date, datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..utils.config import get_connection, get_wita

connection = get_connection().connect()
timestamp_wita = get_wita()

def get_all_laporan_transaksi():
    try:
        result = connection.execute(text("""
            SELECT 
                t.id_transaksi, t.id_kasir, t.id_lokasi, t.id_pelanggan,
                t.tanggal, t.total, t.tunai, t.kembalian,
                COALESCE(h.sisa_hutang, 0) AS sisa_hutang,
                COALESCE(h.status_hutang, 'lunas') AS status_hutang
            FROM transaksi t
            LEFT JOIN hutang h ON t.id_transaksi = h.id_transaksi
            WHERE t.status = 1
            ORDER BY t.tanggal DESC;
        """)).mappings().fetchall()

        data = []
        for row in result:
            row_dict = dict(row)

            if isinstance(row_dict["tanggal"], (date, datetime)):
                row_dict["tanggal"] = row_dict["tanggal"].isoformat()

            id_transaksi = row_dict["id_transaksi"]

            # Hitung modal = SUM(qty × harga_beli) dari detailtransaksi
            modal_result = connection.execute(text("""
                SELECT 
                    SUM(dt.qty * pr.harga_beli) AS total_modal
                FROM detailtransaksi dt
                INNER JOIN produk pr ON dt.id_produk = pr.id_produk
                WHERE dt.id_transaksi = :id_transaksi AND dt.status = 1;
            """), {"id_transaksi": id_transaksi}).scalar()

            modal = modal_result if modal_result else 0
            keuntungan = row_dict["total"] - modal

            row_dict["modal"] = modal
            row_dict["keuntungan"] = keuntungan

            data.append(row_dict)

        return data

    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []
    
def get_laporan_penjualan_item_grouped(id_produk=None, id_lokasi=None):
    try:
        query = """
            SELECT 
                dt.id_produk,
                pr.nama_produk,
                SUM(dt.qty) AS total_qty,
                pr.harga_beli,
                dt.harga_jual,
                SUM(dt.qty * dt.harga_jual) AS subtotal,
                SUM(dt.qty * pr.harga_beli) AS modal,
                SUM((dt.qty * dt.harga_jual) - (dt.qty * pr.harga_beli)) AS keuntungan
            FROM detailtransaksi dt
            INNER JOIN produk pr ON dt.id_produk = pr.id_produk
            INNER JOIN transaksi t ON dt.id_transaksi = t.id_transaksi
            WHERE dt.status = 1 AND t.status = 1
        """
        params = {}

        if id_produk:
            query += " AND dt.id_produk = :id_produk"
            params["id_produk"] = id_produk
        if id_lokasi:
            query += " AND t.id_lokasi = :id_lokasi"
            params["id_lokasi"] = id_lokasi

        query += """
            GROUP BY dt.id_produk, pr.nama_produk, pr.harga_beli, dt.harga_jual
            ORDER BY pr.nama_produk ASC
        """

        result = connection.execute(text(query), params).mappings().fetchall()
        return [dict(row) for row in result]

    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []

def get_laporan_stok(id_produk=None, id_lokasi=None):
    try:
        query = """
            SELECT 
                s.id_lokasi,
                l.nama_lokasi,
                s.id_produk,
                p.nama_produk,
                p.satuan,
                p.harga_beli,
                p.harga_jual,
                s.jumlah AS sisa_stok,
                (s.jumlah * p.harga_beli) AS nilai_modal,
                (s.jumlah * (p.harga_jual - p.harga_beli)) AS potensi_keuntungan
            FROM stok s
            INNER JOIN produk p ON s.id_produk = p.id_produk
            INNER JOIN lokasi l ON s.id_lokasi = l.id_lokasi
            WHERE s.status = 1 AND p.status = 1 AND l.status = 1
        """
        params = {}

        if id_produk:
            query += " AND s.id_produk = :id_produk"
            params["id_produk"] = id_produk

        if id_lokasi:
            query += " AND s.id_lokasi = :id_lokasi"
            params["id_lokasi"] = id_lokasi

        query += " ORDER BY s.id_lokasi, s.id_produk"

        result = connection.execute(text(query), params).mappings().fetchall()
        return [dict(row) for row in result]

    except SQLAlchemyError as e:
        connection.rollback()
        print(f"Error occurred: {str(e)}")
        return []


