from orders.db import get_conn


def get_order(order_id):
    conn = get_conn()
    try:
        rows = conn.run("SELECT id, customer_id, total_cents, status FROM orders WHERE id = %s", (order_id,))
    finally:
        conn.shutdown()
    if not rows:
        return None
    r = rows[0]
    return {"id": r[0], "customer_id": r[1], "total_cents": r[2], "status": r[3]}


def list_orders_for_customer(customer_id):
    conn = get_conn()
    try:
        rows = conn.run("SELECT id, total_cents, status FROM orders WHERE customer_id = %s ORDER BY id", (customer_id,))
    finally:
        conn.shutdown()
    return [{"id": r[0], "total_cents": r[1], "status": r[2]} for r in rows]


def create_order(customer_id, total_cents):
    conn = get_conn()
    try:
        conn.run("INSERT INTO orders (customer_id, total_cents, status) VALUES (%s, %s, 'new')", (customer_id, total_cents))
        new_id = conn.run("SELECT max(id) FROM orders")[0][0]
    finally:
        conn.shutdown()
    return new_id
