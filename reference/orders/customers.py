from orders.db import get_conn


def get_customer(customer_id):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id, name, email FROM customers WHERE id = :id", {"id": customer_id})
    finally:
        conn.close()
    return rows[0] if rows else None


def find_by_email(email):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id FROM customers WHERE lower(email) = lower(:e)", {"e": email})
    finally:
        conn.close()
    return rows[0]["id"] if rows else None
