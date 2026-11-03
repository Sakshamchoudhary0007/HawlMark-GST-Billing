import pytest


@pytest.fixture
def setup_pdf_auth(client):
    res = client.post("/api/auth/register", json={
        "business_name": "PDF Business Ltd",
        "name": "User PDF",
        "email": "pdf.user@example.com",
        "password": "Password123!"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create customer
    c_res = client.post("/api/customers", json={
        "customer_name": "PDF Customer Ltd",
        "gstin": "27AAPFU0939F1ZV",
        "state_code": "27"
    }, headers=headers)
    customer = c_res.json()

    # Create product
    p_res = client.post("/api/products", json={
        "name": "PDF Product",
        "hsn_sac": "9988",
        "unit": "Pcs",
        "default_rate": "100.0000",
        "gst_rate": "18.00"
    }, headers=headers)
    product = p_res.json()

    return {
        "headers": headers,
        "customer": customer,
        "product": product
    }


def test_generate_pdf_for_finalized_invoice(client, setup_pdf_auth):
    headers = setup_pdf_auth["headers"]
    customer = setup_pdf_auth["customer"]
    product = setup_pdf_auth["product"]

    payload = {
        "customer_id": customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "reverse_charge": False,
        "items": [
            {
                "product_id": product["id"],
                "description": "Widget item for PDF",
                "quantity": "2.0000",
                "rate": "100.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00",
                "hsn_sac": "9988"
            }
        ]
    }

    # 1. Create a draft invoice
    resp = client.post("/api/invoices", json=payload, headers=headers)
    assert resp.status_code in [200, 201]
    invoice_id = resp.json()["id"]

    # 2. Finalize the invoice
    fin_resp = client.post(f"/api/invoices/{invoice_id}/finalize", headers=headers)
    assert fin_resp.status_code == 200

    # 3. Request the PDF
    pdf_resp = client.get(f"/api/invoices/{invoice_id}/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["Content-Type"] == "application/pdf"

    # 4. Assert PDF magic number
    content = pdf_resp.content
    assert content.startswith(b"%PDF-"), "Response content must be a valid PDF"


def test_generate_pdf_for_draft_invoice(client, setup_pdf_auth):
    headers = setup_pdf_auth["headers"]
    customer = setup_pdf_auth["customer"]
    product = setup_pdf_auth["product"]

    payload = {
        "customer_id": customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "IGST",
        "reverse_charge": False,
        "items": [
            {
                "product_id": product["id"],
                "description": "Draft Widget",
                "quantity": "1.5000",
                "rate": "200.0000",
                "discount_amount": "10.0000",
                "gst_rate": "12.00",
                "hsn_sac": "1234"
            }
        ]
    }

    # 1. Create a draft invoice
    resp = client.post("/api/invoices", json=payload, headers=headers)
    assert resp.status_code in [200, 201]
    invoice_id = resp.json()["id"]

    # 2. Request the PDF
    pdf_resp = client.get(f"/api/invoices/{invoice_id}/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["Content-Type"] == "application/pdf"

    # 3. Assert PDF magic number
    content = pdf_resp.content
    assert content.startswith(b"%PDF-"), "Response content must be a valid PDF"


def test_generate_pdf_with_query_token(client, setup_pdf_auth):
    token = setup_pdf_auth["headers"]["Authorization"].replace("Bearer ", "")
    headers = setup_pdf_auth["headers"]
    customer = setup_pdf_auth["customer"]
    product = setup_pdf_auth["product"]

    payload = {
        "customer_id": customer["id"],
        "invoice_date": "2026-09-22",
        "tax_mode": "CGST_SGST",
        "reverse_charge": False,
        "items": [
            {
                "product_id": product["id"],
                "description": "Query Token Item",
                "quantity": "1.0000",
                "rate": "500.0000",
                "discount_amount": "0.0000",
                "gst_rate": "18.00",
                "hsn_sac": "9988"
            }
        ]
    }

    resp = client.post("/api/invoices", json=payload, headers=headers)
    assert resp.status_code in [200, 201]
    invoice_id = resp.json()["id"]

    # Request PDF using query parameter token (no Authorization header)
    pdf_resp = client.get(f"/api/invoices/{invoice_id}/pdf?token={token}")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["Content-Type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-")

