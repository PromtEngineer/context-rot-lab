import pathlib

from orders import billing, customers, inventory, orders, reports


def test_get_order():
    assert orders.get_order(1) == {"id": 1, "customer_id": 1, "total_cents": 1200, "status": "paid"}
    assert orders.get_order(99) is None


def test_list_and_create():
    assert [o["id"] for o in orders.list_orders_for_customer(1)] == [1, 2]
    new_id = orders.create_order(2, 300)
    assert orders.get_order(new_id)["total_cents"] == 300


def test_customers():
    assert customers.get_customer(2)["name"] == "Lin"
    assert customers.find_by_email("lin@example.com") == 2


def test_inventory():
    assert inventory.stock_level("A-100") == 5
    assert inventory.reserve("A-100", 2) is True
    assert inventory.stock_level("A-100") == 3
    assert inventory.reserve("B-200", 1) is False


def test_billing():
    assert billing.charge(2) == 800
    assert billing.charge(2) == 0


def test_reports():
    assert reports.daily_revenue("2026-10-01") == 1200


def test_no_legacydb():
    src = pathlib.Path(__file__).parent.parent / "orders"
    offenders = [p.name for p in src.glob("*.py") if "legacydb" in p.read_text()]
    assert offenders == [], f"still uses legacydb: {offenders}"
