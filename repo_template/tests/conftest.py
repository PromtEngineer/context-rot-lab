import os
import sqlite3
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "vendor"))
sys.path.insert(0, ROOT)


@pytest.fixture(autouse=True)
def seeded_db(tmp_path, monkeypatch):
    path = tmp_path / "orders.db"
    c = sqlite3.connect(path)
    c.executescript("""
    CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT);
    CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, total_cents INTEGER, status TEXT, day TEXT);
    CREATE TABLE inventory (sku TEXT PRIMARY KEY, qty INTEGER);
    INSERT INTO customers VALUES (1, 'Ada', 'ada@example.com'), (2, 'Lin', 'Lin@Example.com');
    INSERT INTO orders (customer_id, total_cents, status, day) VALUES
      (1, 1200, 'paid', '2026-10-01'), (1, 800, 'new', '2026-10-01'), (2, 5000, 'paid', '2026-10-02');
    INSERT INTO inventory VALUES ('A-100', 5), ('B-200', 0);
    """)
    c.commit()
    c.close()
    monkeypatch.setenv("ORDERS_DB", str(path))
    yield
