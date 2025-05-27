from sqlalchemy import text
from ..config import get_connection
from datetime import datetime, timedelta

connection = get_connection().connect()

def get_transaction_report(tipe, tanggal, lokasi_id=None):
    # Parse tanggal sebagai datetime object
    date_obj = datetime.strptime(tanggal, "%Y-%m-%d")

    base_where = ""
    params = {}

    if lokasi_id:
        base_where += " AND lokasi_id = :lokasi_id"
        params["lokasi_id"] = lokasi_id

    if tipe == "harian":
        # Filter tanggal persis itu (tanggal tanpa waktu)
        base_where += " AND DATE(tanggal) = :date"
        params["date"] = date_obj.date()

    elif tipe == "mingguan":
        # Cari minggu yang berisi tanggal tersebut (senin sampai minggu)
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        base_where += " AND DATE(tanggal) BETWEEN :start AND :end"
        params["start"] = start_of_week.date()
        params["end"] = end_of_week.date()

    elif tipe == "bulanan":
        # Bulan dan tahun sesuai tanggal
        base_where += " AND EXTRACT(YEAR FROM tanggal) = :year AND EXTRACT(MONTH FROM tanggal) = :month"
        params["year"] = date_obj.year
        params["month"] = date_obj.month

    elif tipe == "tahunan":
        # Tahun sesuai tanggal
        base_where += " AND EXTRACT(YEAR FROM tanggal) = :year"
        params["year"] = date_obj.year

    else:
        raise ValueError("Tipe laporan tidak valid")

    query = text(f"""
        SELECT
            COUNT(*) AS jumlah_transaksi,
            COALESCE(SUM(total),0) AS total_pendapatan,
            COALESCE(SUM(hutang),0) AS total_hutang
        FROM transactions
        WHERE 1=1 {base_where}
    """)

    result = connection.execute(query, params).mappings().fetchone()
    return dict(result)
