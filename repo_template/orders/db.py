"""Connection helper for the orders service."""
import time

import legacydb

from orders.config import DB_HOST, DB_NAME, DB_PORT


def get_conn():
    """Open a database connection.

    The primary flaps for a few hundred milliseconds during failover, so retry
    transient connection failures before giving up.
    """
    last = None
    for attempt in range(3):
        try:
            return legacydb.open(DB_HOST, DB_PORT, DB_NAME)
        except legacydb.ConnectionError as e:
            last = e
            time.sleep(0.01 * (attempt + 1))
    raise last
