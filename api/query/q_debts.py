from sqlalchemy import text
from ..config import get_connection

connection = get_connection().connect()

def add_debt(data):
    query = text("""
        INSERT INTO debts (transaction_id, pelanggan_id, lokasi_id, jumlah_hutang, status, created_at, updated_at)
        VALUES (:transaction_id, :pelanggan_id, :lokasi_id, :jumlah_hutang, 'belum_lunas', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *
    """)
    result = connection.execute(query, data).mappings().fetchone()
    return dict(result)

def get_debts(lokasi_id=None):
    query = """
        SELECT d.*, c.nama AS pelanggan_nama, l.nama AS lokasi_nama
        FROM debts d
        LEFT JOIN customers c ON d.pelanggan_id = c.id
        LEFT JOIN locations l ON d.lokasi_id = l.id
        WHERE 1=1
    """
    params = {}
    if lokasi_id:
        query += " AND d.lokasi_id = :lokasi_id"
        params["lokasi_id"] = lokasi_id

    query += " ORDER BY d.created_at DESC"
    result = connection.execute(text(query), params).mappings().fetchall()
    return [dict(row) for row in result]

def pay_debt(debt_id, amount, kasir_id=None, metode=None, keterangan=None):
    try:
        # Ambil data hutang
        query_get = text("SELECT * FROM debts WHERE id = :debt_id")
        debt = connection.execute(query_get, {"debt_id": debt_id}).mappings().fetchone()
        if not debt:
            return None

        sisa_sebelum = float(debt['jumlah']) - float(debt['jumlah_terbayar'])
        if amount > sisa_sebelum:
            raise ValueError("Jumlah bayar melebihi hutang")

        # Tambahkan riwayat pembayaran
        insert_payment = text("""
            INSERT INTO debt_payments (debt_id, jumlah, kasir_id, metode_pembayaran, keterangan)
            VALUES (:debt_id, :jumlah, :kasir_id, :metode, :keterangan)
        """)
        connection.execute(insert_payment, {
            "debt_id": debt_id,
            "jumlah": amount,
            "kasir_id": kasir_id,
            "metode": metode,
            "keterangan": keterangan
        })

        # Update jumlah_terbayar
        update_debt = text("""
            UPDATE debts
            SET jumlah_terbayar = jumlah_terbayar + :jumlah,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :debt_id
        """)
        connection.execute(update_debt, {"jumlah": amount, "debt_id": debt_id})

        connection.commit()
        return {"status": "success", "message": "Pembayaran berhasil diproses"}
    except Exception as e:
        connection.rollback()
        raise e

def get_debt_payments(debt_id):
    query = text("""
        SELECT dp.*, u.username AS kasir_username
        FROM debt_payments dp
        LEFT JOIN users u ON dp.kasir_id = u.id
        WHERE dp.debt_id = :debt_id
        ORDER BY dp.tanggal ASC
    """)
    result = connection.execute(query, {"debt_id": debt_id}).mappings().fetchall()
    return [dict(row) for row in result]

# Fungsi rekap total hutang
def get_debt_summary(lokasi_id=None):
    query = """
        SELECT
            COALESCE(SUM(jumlah - jumlah_terbayar), 0) AS total_hutang_terutang,
            COUNT(DISTINCT pelanggan_id) AS jumlah_pelanggan_berhutang
        FROM debts
        WHERE (jumlah - jumlah_terbayar) > 0
    """
    params = {}
    if lokasi_id:
        query += " AND lokasi_id = :lokasi_id"
        params["lokasi_id"] = lokasi_id

    result = connection.execute(text(query), params).mappings().fetchone()
    return dict(result)

# Fungsi daftar pelanggan yang memiliki hutang beserta jumlah hutang masing-masing
def get_debtors_list(lokasi_id=None):
    query = """
        SELECT
            c.id AS pelanggan_id,
            c.nama AS pelanggan_nama,
            COALESCE(SUM(d.jumlah - d.jumlah_terbayar), 0) AS total_hutang
        FROM debts d
        JOIN customers c ON d.pelanggan_id = c.id
        WHERE (d.jumlah - d.jumlah_terbayar) > 0
    """
    params = {}
    if lokasi_id:
        query += " AND d.lokasi_id = :lokasi_id"
        params["lokasi_id"] = lokasi_id

    query += """
        GROUP BY c.id, c.nama
        ORDER BY total_hutang DESC
    """

    result = connection.execute(text(query), params).mappings().fetchall()
    return [dict(row) for row in result]