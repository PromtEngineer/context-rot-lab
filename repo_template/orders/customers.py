from orders.db import get_conn


def get_customer(customer_id):
    conn = get_conn()
    try:
        rows = conn.run("SELECT id, name, email FROM customers WHERE id = %s", (customer_id,))
    finally:
        conn.shutdown()
    return {"id": rows[0][0], "name": rows[0][1], "email": rows[0][2]} if rows else None


def find_by_email(email):
    conn = get_conn()
    try:
        rows = conn.run("SELECT id FROM customers WHERE lower(email) = lower(%s)", (email,))
    finally:
        conn.shutdown()
    return rows[0][0] if rows else None
