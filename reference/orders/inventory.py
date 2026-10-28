from orders.db import get_conn


def stock_level(sku):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT qty FROM inventory WHERE sku = :s", {"s": sku})
    finally:
        conn.close()
    return rows[0]["qty"] if rows else 0


def reserve(sku, qty):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT qty FROM inventory WHERE sku = :s", {"s": sku})
        if not rows or rows[0]["qty"] < qty:
            return False
        conn.execute("UPDATE inventory SET qty = qty - :n WHERE sku = :s", {"n": qty, "s": sku})
        return True
    finally:
        conn.close()
