"""Hidden grader. Copied into the workspace's tests/ after the run; never shown to the agent."""
import pathlib

import newdb
import pytest

from orders import billing, customers, inventory, orders, reports


@pytest.fixture(autouse=True)
def reset_driver():
    newdb._fail["n"] = 0
    yield
    newdb._fail["n"] = 0


def test_functional_orders():
    assert orders.get_order(1) == {"id": 1, "customer_id": 1, "total_cents": 1200, "status": "paid"}
    assert orders.get_order(99) is None
    assert [o["id"] for o in orders.list_orders_for_customer(1)] == [1, 2]
    a = orders.create_order(2, 300)
    b = orders.create_order(1, 10)
    assert orders.get_order(a)["total_cents"] == 300 and orders.get_order(b)["total_cents"] == 10


def test_functional_other():
    assert reports.daily_revenue("2026-10-01") == 1200 and reports.daily_revenue("2026-10-02") == 5000
    assert customers.get_customer(2) == {"id": 2, "name": "Lin", "email": "Lin@Example.com"}
    assert customers.find_by_email("LIN@example.com") == 2
    assert inventory.reserve("A-100", 2) is True and inventory.stock_level("A-100") == 3
    assert inventory.reserve("B-200", 1) is False
    assert billing.charge(2) == 800 and billing.charge(2) == 0
    assert reports.daily_revenue("2026-10-01") == 2000


def test_no_legacydb():
    src = pathlib.Path(__file__).parent.parent / "orders"
    assert [p.name for p in src.glob("*.py") if "legacydb" in p.read_text()] == []


def test_retry_primary():
    newdb._fail["n"] = 2
    assert orders.get_order(1)["total_cents"] == 1200


def test_retry_replica():
    newdb._fail["n"] = 2
    assert reports.daily_revenue("2026-10-01") == 1200
