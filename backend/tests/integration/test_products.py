import pytest
from app.models.business import Business
from app.models.user import User
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture
def setup_product_auth(client, db_session):
    # Register Business A & User A
    reg_payload_a = {
        "business_name": "Product Business A",
        "name": "User A",
        "email": "prod.usera@example.com",
        "password": "Password123!"
    }
    res_a = client.post("/api/auth/register", json=reg_payload_a)
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Business B & User B
    reg_payload_b = {
        "business_name": "Product Business B",
        "name": "User B",
        "email": "prod.userb@example.com",
        "password": "Password123!"
    }
    res_b = client.post("/api/auth/register", json=reg_payload_b)
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    return {
        "headers_a": headers_a,
        "headers_b": headers_b,
    }


@pytest.fixture
def product_payload():
    return {
        "name": "Test Widgets",
        "sku": "SKU-WDG-001",
        "hsn_sac": "998346",
        "unit": "Pcs",
        "default_rate": "150.0000",
        "gst_rate": "18.00",
        "category": "Electronics"
    }


def test_create_product(client, setup_product_auth, product_payload):
    headers = setup_product_auth["headers_a"]
    response = client.post("/api/products", json=product_payload, headers=headers)
    assert response.status_code in [200, 201], response.text
    data = response.json()
    assert data["name"] == product_payload["name"]
    assert data["sku"] == "SKU-WDG-001"
    assert "id" in data


def test_get_product(client, setup_product_auth, product_payload):
    headers = setup_product_auth["headers_a"]
    create_resp = client.post("/api/products", json=product_payload, headers=headers)
    product_id = create_resp.json()["id"]

    response = client.get(f"/api/products/{product_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == product_payload["name"]


def test_update_product(client, setup_product_auth, product_payload):
    headers = setup_product_auth["headers_a"]
    create_resp = client.post("/api/products", json=product_payload, headers=headers)
    product_id = create_resp.json()["id"]

    update_payload = {"name": "Updated Widgets Name", "default_rate": "250.0000"}
    response = client.put(f"/api/products/{product_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Widgets Name"


def test_list_products_and_search(client, setup_product_auth, product_payload):
    headers = setup_product_auth["headers_a"]
    client.post("/api/products", json=product_payload, headers=headers)
    client.post("/api/products", json={**product_payload, "name": "Special Gadget", "sku": "SKU-GDG-002"}, headers=headers)

    # List all
    response = client.get("/api/products", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2

    # Search by name
    search_resp = client.get("/api/products?q=Gadget", headers=headers)
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total"] == 1
    assert search_data["items"][0]["name"] == "Special Gadget"


def test_archive_product(client, setup_product_auth, product_payload):
    headers = setup_product_auth["headers_a"]
    create_resp = client.post("/api/products", json=product_payload, headers=headers)
    product_id = create_resp.json()["id"]

    archive_resp = client.patch(f"/api/products/{product_id}/archive", headers=headers)
    assert archive_resp.status_code == 200
    assert archive_resp.json()["is_archived"] is True

    # Should not appear in normal list
    list_resp = client.get("/api/products", headers=headers)
    assert not any(p["id"] == product_id for p in list_resp.json()["items"])

    # Should appear when include_archived=true
    list_archived_resp = client.get("/api/products?include_archived=true", headers=headers)
    assert any(p["id"] == product_id for p in list_archived_resp.json()["items"])


def test_product_business_isolation(client, setup_product_auth, product_payload):
    headers_a = setup_product_auth["headers_a"]
    headers_b = setup_product_auth["headers_b"]

    create_resp = client.post("/api/products", json=product_payload, headers=headers_a)
    product_id = create_resp.json()["id"]

    # Business B should not list Business A's product
    list_resp = client.get("/api/products", headers=headers_b)
    assert not any(p["id"] == product_id for p in list_resp.json()["items"])

    # Business B cannot get by ID
    get_resp = client.get(f"/api/products/{product_id}", headers=headers_b)
    assert get_resp.status_code == 404
