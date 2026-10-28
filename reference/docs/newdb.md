# newdb 1.3 reference

newdb replaces legacydb as the supported driver for the orders service. legacydb 2.4 reaches end of
support next quarter, and the platform team will remove it from the base image.

## Installing

newdb is vendored under `vendor/newdb`. No install step is needed for local development.
The test runner adds `vendor/` to `sys.path`.

## Connecting

```python
import newdb
conn = newdb.connect("postgres://db.internal:5432/orders")
rows = conn.execute("SELECT id, status FROM orders WHERE id = :id", {"id": 42})
conn.close()
```

`connect(dsn, *, retry=None, timeout=5.0)` returns a `Connection`. The DSN takes the form
`postgres://HOST:PORT/DBNAME`. In local development and in tests every DSN resolves to the SQLite
file named by the `ORDERS_DB` environment variable, so you never need to change the DSN for tests.

### Connection retries

`connect()` makes **exactly one** connection attempt by default. If the server is unreachable it
raises `newdb.ConnectError` immediately. Unlike some drivers, newdb never retries a failed
`connect()` on its own: retry behavior is opt-in so that callers can choose their own budget.

To retry, pass a policy:

```python
conn = newdb.connect(DSN, retry=newdb.RetryPolicy(attempts=3, backoff=0.05))
```

`RetryPolicy(attempts=3, backoff=0.05)` makes up to `attempts` tries and sleeps `backoff * n` seconds
between them. You can also keep an application-level retry loop and catch `newdb.ConnectError`.

## Running statements

`Connection.execute(sql, params=None)` runs one statement and returns a **list of dicts**, one per row,
keyed by column name. Writes are committed immediately.

newdb uses **named placeholders** (`:name`) with a dict of parameters. Positional placeholders
(`%s` or `?`) raise `newdb.QueryError`.

```python
conn.execute("UPDATE inventory SET qty = qty - :n WHERE sku = :sku", {"n": 2, "sku": "A-100"})
```

To get the id of an inserted row, use `RETURNING`:

```python
row = conn.execute("INSERT INTO orders (customer_id, total_cents, status) VALUES (:c, :t, 'new') RETURNING id",
                   {"c": 7, "t": 1250})[0]
new_id = row["id"]
```

## Closing

Call `Connection.close()` when you are done. (legacydb called this `shutdown()`.)

## Errors

| Exception | When |
|---|---|
| `newdb.ConnectError` | The connection could not be established. |
| `newdb.QueryError` | The statement failed, or used positional placeholders. |

## Pools

`newdb.Pool(dsn, size=5)` keeps a set of idle connections. The pool health-checks idle connections in
the background. **A failed health check is retried automatically** and the stale connection is
replaced, so pooled connections that went stale recover on their own. `Pool.acquire()` opens a new
connection with a single `connect()` attempt when no idle connection is available. The orders service
does not use pools yet.

## Migrating from legacydb

| legacydb | newdb |
|---|---|
| `legacydb.open(host, port, dbname)` | `newdb.connect("postgres://host:port/dbname")` |
| `conn.run(sql, params_tuple)` with `%s` | `conn.execute(sql, params_dict)` with `:name` |
| rows are tuples | rows are dicts |
| `conn.shutdown()` | `conn.close()` |
| `legacydb.ConnectionError` | `newdb.ConnectError` |
| `cursor.lastrowid` workarounds | `INSERT ... RETURNING id` |

Behavior that callers relied on in legacydb must be preserved explicitly.

## Changelog

- 1.3: `RetryPolicy` backoff is now linear. `Pool` health checks retry automatically.
- 1.2: `QueryError` now wraps the underlying driver error.
- 1.1: Named placeholders only.
- 1.0: First release.
