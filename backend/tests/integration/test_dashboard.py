import pytest
from datetime import date
from decimal import Decimal

from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.product import Product


@pytest.fixture
def setup_dashboard_auth(client):
    res = client.post("/api/auth/register", json={
        "business_name": "Dashboard Business",
        "name": "Dashboard Owner",
        "email": "dash.owner@example.com",
        "password": "Password123!"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch user info to get business_id and user_id
    me_res = client.get("/api/auth/me", headers=headers)
    user_info = me_res.json()

    return {
        "headers": headers,
        "business_id": user_info["business_id"],
        "user_id": user_info["id"]
    }


def test_get_dashboard_summary(client, setup_dashboard_auth, db_session):
    headers = setup_dashboard_auth["headers"]
    business_id = setup_dashboard_auth["business_id"]
    user_id = setup_dashboard_auth["user_id"]

    # Create active customer
    cust = Customer(
        business_id=business_id,
        customer_name="Test Dashboard Customer",
        is_archived=False
    )
    db_session.add(cust)

    # Create active product
    prod = Product(
        business_id=business_id,
        name="Test Dashboard Product",
        default_rate=Decimal("100.0000"),
        is_archived=False
    )
    db_session.add(prod)

    # Create invoices
    inv_final = Invoice(
        business_id=business_id,
        invoice_number="INV-D-001",
        invoice_date=date.today(),
        grand_total=Decimal("500.0000"),
        status="FINALIZED",
        created_by=user_id
    )
    inv_draft = Invoice(
        business_id=business_id,
        invoice_number="INV-D-002",
        invoice_date=date.today(),
        grand_total=Decimal("250.0000"),
        status="DRAFT",
        created_by=user_id
    )
    db_session.add(inv_final)
    db_session.add(inv_draft)
    db_session.commit()

    # Hit the dashboard API
    response = client.get("/api/dashboard/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "total_revenue" in data
    # Only FINALIZED invoices count towards total revenue
    assert Decimal(str(data["total_revenue"])) == Decimal("500.0000")

    assert data["total_invoices"] >= 2
    assert data["total_customers"] >= 1
    assert data["total_products"] >= 1

    assert len(data["recent_invoices"]) >= 2
    assert "monthly_revenue" in data
    assert len(data["monthly_revenue"]) == 6
