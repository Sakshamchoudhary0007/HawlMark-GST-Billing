import pytest
from app.models.business import Business
from app.models.user import User
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture
def setup_invoice_auth(client, db_session):
    # Register Business A & User A
    res_a = client.post("/api/auth/register", json={
        "business_name": "Invoice Business A",
        "name": "User A",
        "email": "inv.usera@example.com",
        "password": "Password123!"
    })
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Business B & User B
    res_b = client.post("/api/auth/register", json={
        "business_name": "Invoice Business B",
        "name": "User B",
        "email": "inv.userb@example.com",
        "password": "Password123!"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    return {
        "headers_a": headers_a,
        "headers_b": headers_b,
    }


@pytest.fixture
def test_customer(client, setup_invoice_auth):
    headers = setup_invoice_auth["headers_a"]
    res = client.post("/api/customers", json={
        "customer_name": "Acme Customer Ltd",
        "gstin": "27AAPFU0939F1ZV",
        "state_code": "27",
        "address_line1": "123 Old Address Street"
    }, headers=headers)
    return res.json()


@pytest.fixture
def test_product(client, setup_invoice_auth):
    headers = setup_invoice_auth["headers_a"]
    res = client.post("/api/products", json={
        "name": "Widget A",
        "hsn_sac": "998346",
        "unit": "Pcs",
        "default_rate": "100.0000",
        "gst_rate": "18.00"
    }, headers=headers)
    return res.json()


def test_create_draft_invoice(client, setup_invoice_auth, test_customer, test_product):
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "reverse_charge": False,
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Widget A item",
                "quantity": "2.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }

    response = client.post("/api/invoices", json=payload, headers=headers)
    assert response.status_code in [200, 201], response.text
    data = response.json()
    assert data["status"] == "DRAFT"
    assert data["subtotal"] == "200.0000"
    assert data["taxable_amount"] == "200.0000"
    assert data["cgst_amount"] == "18.0000"
    assert data["sgst_amount"] == "18.0000"
    assert data["grand_total"] == "236.0000"


def test_update_draft_invoice(client, setup_invoice_auth, test_customer, test_product):
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "reverse_charge": False,
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Widget item",
                "quantity": "2.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers)
    invoice_id = resp.json()["id"]

    update_payload = {
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Updated item",
                "quantity": "3.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    response = client.put(f"/api/invoices/{invoice_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == "300.0000"
    assert data["taxable_amount"] == "300.0000"
    assert data["cgst_amount"] == "27.0000"
    assert data["sgst_amount"] == "27.0000"
    assert data["grand_total"] == "354.0000"


def test_finalize_invoice(client, setup_invoice_auth, test_customer, test_product):
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "reverse_charge": False,
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Widget item",
                "quantity": "2.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers)
    invoice_id = resp.json()["id"]

    response = client.post(f"/api/invoices/{invoice_id}/finalize", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FINALIZED"
    assert data["invoice_number"] is not None
    assert data["customer_snapshot"] is not None
    assert data["seller_snapshot"] is not None
    assert data["customer_snapshot"]["customer_name"] == "Acme Customer Ltd"


def test_edit_finalized_invoice_fails(client, setup_invoice_auth, test_customer, test_product):
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Widget item",
                "quantity": "1.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers)
    invoice_id = resp.json()["id"]
    client.post(f"/api/invoices/{invoice_id}/finalize", headers=headers)

    update_payload = {"notes": "trying to update finalized invoice"}
    response = client.put(f"/api/invoices/{invoice_id}", json=update_payload, headers=headers)
    assert response.status_code == 400


def test_historical_snapshot_integrity(client, setup_invoice_auth, test_customer, test_product):
    """Verify that changing customer master later DOES NOT alter old finalized invoice snapshot."""
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Item 1",
                "quantity": "1.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers)
    invoice_id = resp.json()["id"]
    client.post(f"/api/invoices/{invoice_id}/finalize", headers=headers)

    # Update customer master record address & name
    client.put(f"/api/customers/{test_customer['id']}", json={
        "customer_name": "New Changed Name",
        "address_line1": "456 New Street Address"
    }, headers=headers)

    # Fetch finalized invoice -> snapshot MUST still have old customer data
    res_inv = client.get(f"/api/invoices/{invoice_id}", headers=headers)
    data = res_inv.json()
    assert data["customer_snapshot"]["customer_name"] == "Acme Customer Ltd"
    assert data["customer_snapshot"]["address_line1"] == "123 Old Address Street"


def test_cancel_invoice(client, setup_invoice_auth, test_customer, test_product):
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Widget item",
                "quantity": "1.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers)
    invoice_id = resp.json()["id"]

    response = client.post(f"/api/invoices/{invoice_id}/cancel", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_invoice_business_isolation(client, setup_invoice_auth, test_customer, test_product):
    headers_a = setup_invoice_auth["headers_a"]
    headers_b = setup_invoice_auth["headers_b"]

    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Widget item",
                "quantity": "1.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers_a)
    invoice_id = resp.json()["id"]

    # Business B attempts to retrieve Business A's invoice -> MUST return 404
    get_b = client.get(f"/api/invoices/{invoice_id}", headers=headers_b)
    assert get_b.status_code == 404

    # Business B attempts to list invoices -> MUST NOT include Business A's invoice
    list_b = client.get("/api/invoices", headers=headers_b)
    assert not any(inv["id"] == invoice_id for inv in list_b.json()["items"])


def test_delete_invoice(client, setup_invoice_auth, test_customer, test_product):
    headers = setup_invoice_auth["headers_a"]
    payload = {
        "customer_id": test_customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "items": [
            {
                "product_id": test_product["id"],
                "description": "Item to delete",
                "quantity": "1.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00"
            }
        ]
    }
    resp = client.post("/api/invoices", json=payload, headers=headers)
    invoice_id = resp.json()["id"]

    del_resp = client.delete(f"/api/invoices/{invoice_id}", headers=headers)
    assert del_resp.status_code == 200

    # Verify 404 when querying deleted invoice
    get_resp = client.get(f"/api/invoices/{invoice_id}", headers=headers)
    assert get_resp.status_code == 404

