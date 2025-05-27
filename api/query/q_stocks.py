from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ..config import get_connection

connection = get_connection().connect()

def get_stocks(product_id=None, location_id=None):
    query = "SELECT * FROM stocks WHERE 1=1"
    params = {}
    if product_id:
        query += " AND product_id = :product_id"
        params["product_id"] = product_id
    if location_id:
        query += " AND location_id = :location_id"
        params["location_id"] = location_id

    result = connection.execute(text(query), params).mappings().fetchall()
    return [dict(row) for row in result]

def get_stock_detail(product_id, location_id):
    query = text("SELECT * FROM stocks WHERE product_id = :product_id AND location_id = :location_id")
    result = connection.execute(query, {"product_id": product_id, "location_id": location_id}).mappings().fetchone()
    return dict(result) if result else None

def add_stock(data):
    existing = get_stock_detail(data['product_id'], data['location_id'])
    if existing:
        query = text("""
            UPDATE stocks SET jumlah = jumlah + :jumlah
            WHERE product_id = :product_id AND location_id = :location_id
            RETURNING *
        """)
    else:
        query = text("""
            INSERT INTO stocks (product_id, location_id, jumlah)
            VALUES (:product_id, :location_id, :jumlah)
            RETURNING *
        """)
    result = connection.execute(query, data).mappings().fetchone()

    # Log ke stock_history
    log_query = text("""
        INSERT INTO stock_history (product_id, location_id, jumlah, tipe, keterangan)
        VALUES (:product_id, :location_id, :jumlah, :tipe, :keterangan)
    """)
    connection.execute(log_query, {
        "product_id": data["product_id"],
        "location_id": data["location_id"],
        "jumlah": data["jumlah"],
        "tipe": "in",
        "keterangan": data.get("keterangan", "Stok Masuk")
    })

    connection.commit()
    return dict(result)

def reduce_stock(data):
    existing = get_stock_detail(data['product_id'], data['location_id'])
    if not existing or float(existing['jumlah']) < float(data['jumlah']):
        return None

    query = text("""
        UPDATE stocks SET jumlah = jumlah - :jumlah
        WHERE product_id = :product_id AND location_id = :location_id
        RETURNING *
    """)
    result = connection.execute(query, data).mappings().fetchone()

    # Log ke stock_history
    log_query = text("""
        INSERT INTO stock_history (product_id, location_id, jumlah, tipe, keterangan)
        VALUES (:product_id, :location_id, :jumlah, :tipe, :keterangan)
    """)
    connection.execute(log_query, {
        "product_id": data["product_id"],
        "location_id": data["location_id"],
        "jumlah": data["jumlah"],
        "tipe": "out",
        "keterangan": data.get("keterangan", "Stok Keluar")
    })

    connection.commit()
    return dict(result)

def transfer_stock(data):
    reduce_data = {
        "product_id": data['product_id'],
        "location_id": data['from_location'],
        "jumlah": data['jumlah'],
        "keterangan": data.get("keterangan", "Transfer keluar ke lokasi " + str(data['to_location']))
    }
    add_data = {
        "product_id": data['product_id'],
        "location_id": data['to_location'],
        "jumlah": data['jumlah'],
        "keterangan": data.get("keterangan", "Transfer masuk dari lokasi " + str(data['from_location']))
    }
    reduced = reduce_stock(reduce_data)
    if reduced is None:
        raise SQLAlchemyError("Stock tidak mencukupi untuk transfer")
    added = add_stock(add_data)
    connection.commit()
    return {"dari": reduced, "ke": added}

def get_stock_history(product_id=None, location_id=None, start_date=None, end_date=None):
    query = """
        SELECT * FROM stock_history
        WHERE 1=1
    """
    params = {}

    if product_id:
        query += " AND product_id = :product_id"
        params["product_id"] = product_id
    if location_id:
        query += " AND location_id = :location_id"
        params["location_id"] = location_id
    if start_date:
        query += " AND created_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND created_at <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY created_at DESC"

    try:
        result = connection.execute(text(query), params).mappings().fetchall()
        return [dict(row) for row in result]
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return []

def perform_stock_opname(data):
    current = get_stock_detail(data['product_id'], data['location_id'])
    if not current:
        return None
    jumlah_sistem = float(current['jumlah'])
    jumlah_fisik = float(data['jumlah_fisik'])
    if jumlah_fisik < 0:
        return None  # atau raise error
    selisih = jumlah_fisik - jumlah_sistem

    update_query = text("""
        UPDATE stocks SET jumlah = :jumlah_fisik
        WHERE product_id = :product_id AND location_id = :location_id
        RETURNING *
    """)
    log_query = text("""
        INSERT INTO stock_opname_logs (product_id, location_id, jumlah_sistem, jumlah_fisik, selisih, keterangan, created_at)
        VALUES (:product_id, :location_id, :jumlah_sistem, :jumlah_fisik, :selisih, :keterangan, CURRENT_TIMESTAMP)
    """)

    connection.execute(update_query, {
        "jumlah_fisik": jumlah_fisik,
        "product_id": data['product_id'],
        "location_id": data['location_id']
    })
    connection.execute(log_query, {
        **data,
        "jumlah_sistem": jumlah_sistem,
        "selisih": selisih
    })
    connection.commit()
    return {
        "product_id": data['product_id'],
        "location_id": data['location_id'],
        "jumlah_sistem": jumlah_sistem,
        "jumlah_fisik": jumlah_fisik,
        "selisih": selisih
    }

def get_opname_logs(product_id=None, location_id=None):
    query = "SELECT * FROM stock_opname_logs WHERE 1=1"
    params = {}

    if product_id:
        query += " AND product_id = :product_id"
        params["product_id"] = product_id
    if location_id:
        query += " AND location_id = :location_id"
        params["location_id"] = location_id

    query += " ORDER BY created_at DESC"

    result = connection.execute(text(query), params).mappings().fetchall()
    return [dict(row) for row in result]
