"""Connection helper for the orders service."""
import newdb

from orders.config import DB_HOST, DB_NAME, DB_PORT

DSN = f"postgres://{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_conn():
    """Open a connection, retrying transient failures (the primary flaps during failover)."""
    return newdb.connect(DSN, retry=newdb.RetryPolicy(attempts=3, backoff=0.01))
