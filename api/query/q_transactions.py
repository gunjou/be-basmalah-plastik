from sqlalchemy import text
from ..config import get_connection
from .q_debts import add_debt  # pastikan file q_debts.py sudah ada

connection = get_connection().connect()

def add_transaction(data, items):
    # Simpan transaksi
    query_trx = text("""
        INSERT INTO transactions (tanggal, lokasi_id, kasir_id, pelanggan_id, total, tunai, kembalian)
        VALUES (:tanggal, :lokasi_id, :kasir_id, :pelanggan_id, :total, :tunai, :kembalian)
        RETURNING id, tanggal, lokasi_id, kasir_id, pelanggan_id, total, tunai, kembalian
    """)
    trx = connection.execute(query_trx, data).mappings().fetchone()

    # Simpan item transaksi
    query_item = text("""
        INSERT INTO transaction_items (transaction_id, product_id, jumlah, harga, subtotal)
        VALUES (:transaction_id, :product_id, :jumlah, :harga, :subtotal)
    """)
    for item in items:
        connection.execute(query_item, {
            "transaction_id": trx['id'],
            "product_id": item['product_id'],
            "jumlah": item['jumlah'],
            "harga": item['harga'],
            "subtotal": item['subtotal']
        })

    # Jika tunai < total, buat entri hutang
    if data["tunai"] < data["total"] and data["pelanggan_id"]:
        debt_data = {
            "transaction_id": trx["id"],
            "customer_id": data["pelanggan_id"],
            "jumlah": data["total"] - data["tunai"]
        }
        add_debt(debt_data)

    connection.commit()
    return dict(trx)

def get_transaction_detail(transaction_id):
    # Ambil data transaksi lengkap
    query_trx = text("""
        SELECT t.*, c.nama AS pelanggan_nama, u.username AS kasir_username, l.nama AS lokasi_nama
        FROM transactions t
        LEFT JOIN customers c ON t.pelanggan_id = c.id
        LEFT JOIN users u ON t.kasir_id = u.id
        LEFT JOIN locations l ON t.lokasi_id = l.id
        WHERE t.id = :transaction_id
    """)
    trx = connection.execute(query_trx, {"transaction_id": transaction_id}).mappings().fetchone()
    if not trx:
        return None

    # Ambil item transaksinya
    query_items = text("""
        SELECT ti.*, p.nama AS product_nama
        FROM transaction_items ti
        LEFT JOIN products p ON ti.product_id = p.id
        WHERE ti.transaction_id = :transaction_id
    """)
    items = connection.execute(query_items, {"transaction_id": transaction_id}).mappings().fetchall()

    return {
        "transaction": dict(trx),
        "items": [dict(i) for i in items]
    }

def get_invoice_data(transaction_id):
    return get_transaction_detail(transaction_id)
