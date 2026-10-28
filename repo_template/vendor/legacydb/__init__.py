"""legacydb 2.4: the old in-house database driver (being retired)."""
import os
import sqlite3


class ConnectionError(Exception):
    """Raised when the server refuses or drops the connection."""


_fail = {"n": 0}  # test hook: number of upcoming open() calls that fail


def open(host, port, dbname):
    """Open a connection. Makes a single attempt."""
    if _fail["n"] > 0:
        _fail["n"] -= 1
        raise ConnectionError(f"legacydb: connection to {host}:{port}/{dbname} refused")
    return LegacyConnection(os.environ["ORDERS_DB"])


class LegacyConnection:
    def __init__(self, path):
        self._c = sqlite3.connect(path)

    def run(self, sql, params=()):
        """Run SQL with %s positional placeholders. Returns a list of tuples."""
        cur = self._c.execute(sql.replace("%s", "?"), tuple(params))
        self._c.commit()
        return cur.fetchall()

    def shutdown(self):
        self._c.close()
