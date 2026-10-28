"""Reporting queries. These run against the read replica."""
import time

import legacydb

from orders.config import DB_NAME, DB_PORT

REPLICA_HOST = "db-replica.internal"


def daily_revenue(day):
    """Total paid revenue in cents for a YYYY-MM-DD day.

    The replica drops new connections under load, so try up to 3 times.
    """
    last = None
    for attempt in range(3):
        try:
            conn = legacydb.open(REPLICA_HOST, DB_PORT, DB_NAME)
        except legacydb.ConnectionError as e:
            last = e
            time.sleep(0.01 * (attempt + 1))
            continue
        try:
            rows = conn.run("SELECT coalesce(sum(total_cents), 0) FROM orders WHERE status = 'paid' AND day = %s", (day,))
            return rows[0][0]
        finally:
            conn.shutdown()
    raise last
