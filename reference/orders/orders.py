from orders.db import get_conn


def get_order(order_id):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id, customer_id, total_cents, status FROM orders WHERE id = :id", {"id": order_id})
    finally:
        conn.close()
    return rows[0] if rows else None


def list_orders_for_customer(customer_id):
    conn = get_conn()
    try:
        return conn.execute("SELECT id, total_cents, status FROM orders WHERE customer_id = :c ORDER BY id", {"c": customer_id})
    finally:
        conn.close()


def create_order(customer_id, total_cents):
    conn = get_conn()
    try:
        return conn.execute("INSERT INTO orders (customer_id, total_cents, status) VALUES (:c, :t, 'new') RETURNING id", {"c": customer_id, "t": total_cents})[0]["id"]
    finally:
        conn.close()
