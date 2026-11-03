import pytest
from app.models.business import Business
from app.models.user import User
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture
def setup_customer_auth(client, db_session):
    # Register Business A & User A
    reg_payload_a = {
        "business_name": "Business A",
        "name": "User A",
        "email": "user.a@example.com",
        "password": "Password123!"
    }
    res_a = client.post("/api/auth/register", json=reg_payload_a)
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Business B & User B
    reg_payload_b = {
        "business_name": "Business B",
        "name": "User B",
        "email": "user.b@example.com",
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
def test_customer_data():
    return {
        "customer_name": "Test Customer Inc",
        "gstin": "27AAPFU0939F1ZV",
        "mobile": "9876543210",
        "licence_number": "LIC12345",
        "email": "customer@example.com",
        "city": "Mumbai",
        "state": "Maharashtra",
        "state_code": "27"
    }


def test_create_customer(client, setup_customer_auth, test_customer_data):
    headers = setup_customer_auth["headers_a"]
    response = client.post("/api/customers", json=test_customer_data, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["customer_name"] == test_customer_data["customer_name"]
    assert "id" in data
    assert data["business_id"] is not None


def test_get_customer(client, setup_customer_auth, test_customer_data):
    headers = setup_customer_auth["headers_a"]
    create_response = client.post("/api/customers", json=test_customer_data, headers=headers)
    customer_id = create_response.json()["id"]

    response = client.get(f"/api/customers/{customer_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["customer_name"] == test_customer_data["customer_name"]


def test_update_customer(client, setup_customer_auth, test_customer_data):
    headers = setup_customer_auth["headers_a"]
    create_response = client.post("/api/customers", json=test_customer_data, headers=headers)
    customer_id = create_response.json()["id"]

    update_data = {"customer_name": "Updated Customer Name", "mobile": "9999999999"}
    response = client.put(f"/api/customers/{customer_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Updated Customer Name"
    assert data["mobile"] == "9999999999"


def test_list_customers_and_search(client, setup_customer_auth, test_customer_data):
    headers = setup_customer_auth["headers_a"]
    client.post("/api/customers", json=test_customer_data, headers=headers)
    client.post("/api/customers", json={"customer_name": "Another Company", "gstin": "07AAACH7409R1ZZ"}, headers=headers)

    # List all
    response = client.get("/api/customers", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2

    # Search by name
    search_response = client.get("/api/customers?q=Another", headers=headers)
    search_data = search_response.json()
    assert search_data["total"] == 1
    assert search_data["items"][0]["customer_name"] == "Another Company"

    # Search by GSTIN
    search_gstin = client.get("/api/customers?q=27AAPFU", headers=headers)
    assert search_gstin.json()["total"] >= 1


def test_archive_customer(client, setup_customer_auth, test_customer_data):
    headers = setup_customer_auth["headers_a"]
    create_response = client.post("/api/customers", json=test_customer_data, headers=headers)
    customer_id = create_response.json()["id"]

    archive_response = client.patch(f"/api/customers/{customer_id}/archive?archive=true", headers=headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["is_archived"] is True

    # Check it doesn't appear in normal list
    list_response = client.get("/api/customers", headers=headers)
    items = list_response.json()["items"]
    assert not any(c["id"] == customer_id for c in items)

    # Check it appears if included
    list_archived = client.get("/api/customers?include_archived=true", headers=headers)
    items_archived = list_archived.json()["items"]
    assert any(c["id"] == customer_id for c in items_archived)


def test_mandatory_business_isolation(client, setup_customer_auth, test_customer_data):
    """MANDATORY SECURITY TEST: Business B cannot access or modify Business A's customer."""
    headers_a = setup_customer_auth["headers_a"]
    headers_b = setup_customer_auth["headers_b"]

    # User A creates customer
    create_resp = client.post("/api/customers", json=test_customer_data, headers=headers_a)
    assert create_resp.status_code == 200
    customer_id = create_resp.json()["id"]

    # User B attempts GET
    get_resp = client.get(f"/api/customers/{customer_id}", headers=headers_b)
    assert get_resp.status_code in [404, 403]

    # User B attempts PUT
    put_resp = client.put(f"/api/customers/{customer_id}", json={"customer_name": "Hacked Name"}, headers=headers_b)
    assert put_resp.status_code in [404, 403]

    # User B attempts ARCHIVE
    archive_resp = client.patch(f"/api/customers/{customer_id}/archive?archive=true", headers=headers_b)
    assert archive_resp.status_code in [404, 403]

    # User B lists customers -> should NOT see User A's customer
    list_resp = client.get("/api/customers", headers=headers_b)
    items = list_resp.json()["items"]
    assert not any(c["id"] == customer_id for c in items)


def test_delete_customer(client, setup_customer_auth, test_customer_data):
    headers = setup_customer_auth["headers_a"]
    create_response = client.post("/api/customers", json=test_customer_data, headers=headers)
    customer_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/customers/{customer_id}", headers=headers)
    assert delete_response.status_code == 200

    # Verify 404 when querying deleted customer
    get_response = client.get(f"/api/customers/{customer_id}", headers=headers)
    assert get_response.status_code == 404

