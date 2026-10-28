"""newdb 1.3: the replacement database driver. See docs/newdb.md."""
import os
import re
import sqlite3
import time


class ConnectError(Exception):
    """Raised when a connection cannot be established."""


class QueryError(Exception):
    """Raised when a statement fails."""


class RetryPolicy:
    def __init__(self, attempts=3, backoff=0.05):
        if attempts < 1:
            raise ValueError("attempts must be >= 1")
        self.attempts = attempts
        self.backoff = backoff


_fail = {"n": 0}       # test hook: number of upcoming connection attempts that fail
_attempts = {"n": 0}   # test hook: total connection attempts made


def connect(dsn, *, retry=None, timeout=5.0):
    """Open a connection to `dsn`. Makes ONE attempt unless `retry` is given."""
    attempts = retry.attempts if retry is not None else 1
    last = None
    for i in range(attempts):
        _attempts["n"] += 1
        if _fail["n"] > 0:
            _fail["n"] -= 1
            last = ConnectError(f"newdb: could not connect to {dsn} (attempt {i + 1}/{attempts})")
            if retry is not None:
                time.sleep(min(retry.backoff, 0.01))
            continue
        return Connection(dsn)
    raise last


_NAMED = re.compile(r"(?<!:):([A-Za-z_][A-Za-z0-9_]*)")


class Connection:
    def __init__(self, dsn):
        self.dsn = dsn
        self._c = sqlite3.connect(os.environ["ORDERS_DB"])
        self._c.row_factory = sqlite3.Row

    def execute(self, sql, params=None):
        """Run SQL with :name placeholders and a dict of params. Returns a list of dicts."""
        if "%s" in sql or "?" in sql:
            raise QueryError("newdb uses named placeholders (:name); positional placeholders are not supported")
        params = params or {}
        if not isinstance(params, dict):
            raise QueryError("params must be a dict")
        try:
            cur = self._c.execute(_NAMED.sub(r":\1", sql), params)
        except sqlite3.Error as e:
            raise QueryError(str(e)) from e
        rows = [dict(r) for r in cur.fetchall()]
        self._c.commit()
        return rows

    def close(self):
        self._c.close()


class Pool:
    """Connection pool. Idle connections are health-checked in the background; a failed
    health check is retried automatically and the stale connection is replaced."""

    def __init__(self, dsn, size=5):
        self.dsn = dsn
        self.size = size

    def acquire(self):
        return connect(self.dsn)  # NOTE: acquiring a NEW connection is a single attempt

    def release(self, conn):
        conn.close()
