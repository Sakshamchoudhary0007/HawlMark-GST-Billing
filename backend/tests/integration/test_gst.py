import pytest
from fastapi.testclient import TestClient
from app.models.business import Business
from app.models.user import User
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


def get_auth_headers(client: TestClient, db_session):
    b = Business(legal_name="GST Test Business")
    db_session.add(b)
    db_session.commit()

    user = User(
        email="gst_test@example.com",
        password_hash=hash_password("Password123!"),
        name="GST Test User",
        is_active=True,
        business_id=b.id,
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "business_id": user.business_id, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def test_gst_lookup_valid(client: TestClient, db_session):
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/gst/lookup?gstin=27AAPFU0939F1ZV", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["gstin"] == "27AAPFU0939F1ZV"
    assert data["state_code"] == "27"
    assert data["state"] == "Maharashtra"
    assert data["taxpayer_type"] == "Regular"
    assert data["status"] == "Active"


def test_gst_lookup_invalid_format(client: TestClient, db_session):
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/gst/lookup?gstin=INVALID123", headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "GST_INVALID_FORMAT"


def test_gst_lookup_not_found(client: TestClient, db_session):
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/gst/lookup?gstin=27AAPFU0939F999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "GST_NOT_FOUND"


def test_gst_lookup_timeout(client: TestClient, db_session):
    headers = get_auth_headers(client, db_session)
    response = client.get("/api/gst/lookup?gstin=27AAPFU0939F888", headers=headers)
    assert response.status_code == 504
    data = response.json()
    assert data["error"]["code"] == "GST_TIMEOUT"


def test_gst_lookup_unauthorized(client: TestClient):
    response = client.get("/api/gst/lookup?gstin=27AAPFU0939F1ZV")
    assert response.status_code == 401
