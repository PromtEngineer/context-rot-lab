import newdb

from orders.config import DB_NAME, DB_PORT

DSN = f"postgres://db-replica.internal:{DB_PORT}/{DB_NAME}"


def daily_revenue(day):
    conn = newdb.connect(DSN, retry=newdb.RetryPolicy(attempts=3, backoff=0.01))
    try:
        return conn.execute("SELECT coalesce(sum(total_cents), 0) AS t FROM orders WHERE status = 'paid' AND day = :day", {"day": day})[0]["t"]
    finally:
        conn.close()
