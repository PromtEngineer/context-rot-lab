from orders.db import get_conn


def charge(order_id):
    """Mark an order as paid and return the amount charged in cents."""
    conn = get_conn()
    try:
        rows = conn.run("SELECT total_cents, status FROM orders WHERE id = %s", (order_id,))
        if not rows:
            raise KeyError(order_id)
        total, status = rows[0]
        if status == "paid":
            return 0
        conn.run("UPDATE orders SET status = 'paid' WHERE id = %s", (order_id,))
        return total
    finally:
        conn.shutdown()
