from orders.db import get_conn


def stock_level(sku):
    conn = get_conn()
    try:
        rows = conn.run("SELECT qty FROM inventory WHERE sku = %s", (sku,))
    finally:
        conn.shutdown()
    return rows[0][0] if rows else 0


def reserve(sku, qty):
    """Reserve stock. Returns True if there was enough."""
    conn = get_conn()
    try:
        rows = conn.run("SELECT qty FROM inventory WHERE sku = %s", (sku,))
        if not rows or rows[0][0] < qty:
            return False
        conn.run("UPDATE inventory SET qty = qty - %s WHERE sku = %s", (qty, sku))
        return True
    finally:
        conn.shutdown()
