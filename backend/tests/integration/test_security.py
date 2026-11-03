import pytest
from fastapi.testclient import TestClient


def create_business_and_user(client: TestClient, b_name: str, u_email: str) -> dict:
    # Register business
    resp = client.post("/api/auth/register", json={
        "business_name": b_name,
        "name": "Admin Owner",
        "email": u_email,
        "password": "Password123!"
    })
    data = resp.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    b_resp = client.get("/api/business", headers=headers)
    b_id = b_resp.json()["id"]

    return {"token": token, "headers": headers, "business_id": b_id, "email": u_email}


def test_audit_logs_admin_and_non_admin(client: TestClient):
    b1 = create_business_and_user(client, "Audit Biz 1", "admin.audit@b1.com")
    headers_admin = b1["headers"]

    # Admin creates customer
    client.post("/api/customers", headers=headers_admin, json={
        "customer_name": "Cust Audit 1",
        "email": "c1@b1.com",
        "mobile": "9999999999",
        "state": "Maharashtra",
        "state_code": "27"
    })

    # Admin creates staff user
    client.post("/api/users", headers=headers_admin, json={
        "name": "Staff Audit User",
        "email": "staff.audit@b1.com",
        "password": "Password123!",
        "role": "staff"
    })

    # Login as staff user
    staff_login = client.post("/api/auth/login", json={
        "email": "staff.audit@b1.com",
        "password": "Password123!"
    })
    staff_token = staff_login.json()["access_token"]
    headers_staff = {"Authorization": f"Bearer {staff_token}"}

    # Admin gets audit logs -> 200 OK
    a_resp = client.get("/api/audit-logs", headers=headers_admin)
    assert a_resp.status_code == 200
    logs = a_resp.json()["items"]
    assert isinstance(logs, list)

    # Non-admin staff gets audit logs -> 403 Forbidden
    a_resp_staff = client.get("/api/audit-logs", headers=headers_staff)
    assert a_resp_staff.status_code == 403


def test_security_isolation(client: TestClient):
    """MANDATORY SECURITY ISOLATION TEST: Tenant B cannot access Tenant A's objects."""
    b1 = create_business_and_user(client, "Sec Business A", "sec.admin.a@b1.com")
    b2 = create_business_and_user(client, "Sec Business B", "sec.admin.b@b2.com")

    # B1 creates customer, product, invoice
    c_resp = client.post("/api/customers", headers=b1["headers"], json={
        "customer_name": "B1 Secret Customer", "state": "Maharashtra", "state_code": "27"
    })
    c_id = c_resp.json()["id"]

    p_resp = client.post("/api/products", headers=b1["headers"], json={
        "name": "B1 Secret Product", "hsn_sac": "1234", "default_rate": "100.0000", "gst_rate": "18.00"
    })
    p_id = p_resp.json()["id"]

    inv_resp = client.post("/api/invoices", headers=b1["headers"], json={
        "customer_id": c_id,
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "items": [{"product_id": p_id, "description": "Sec Item", "quantity": "1.0000", "rate": "100.0000", "gst_rate": "18.00"}]
    })
    inv_id = inv_resp.json()["id"]

    # B2 attempts to access B1's customer -> 404
    b2_c = client.get(f"/api/customers/{c_id}", headers=b2["headers"])
    assert b2_c.status_code in [403, 404]

    # B2 attempts to access B1's product -> 404
    b2_p = client.get(f"/api/products/{p_id}", headers=b2["headers"])
    assert b2_p.status_code in [403, 404]

    # B2 attempts to access B1's invoice -> 404
    b2_inv = client.get(f"/api/invoices/{inv_id}", headers=b2["headers"])
    assert b2_inv.status_code in [403, 404]

    # B2 audit logs should ONLY contain B2's logs
    b2_logs = client.get("/api/audit-logs", headers=b2["headers"])
    for log in b2_logs.json()["items"]:
        assert log["business_id"] == b2["business_id"]
