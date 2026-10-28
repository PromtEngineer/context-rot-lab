from orders.db import get_conn


def charge(order_id):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT total_cents, status FROM orders WHERE id = :id", {"id": order_id})
        if not rows:
            raise KeyError(order_id)
        if rows[0]["status"] == "paid":
            return 0
        conn.execute("UPDATE orders SET status = 'paid' WHERE id = :id", {"id": order_id})
        return rows[0]["total_cents"]
    finally:
        conn.close()
