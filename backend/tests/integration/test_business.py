import pytest
from app.models.business import Business
from app.models.user import User
from app.auth.password import hash_password
from app.auth.jwt import create_access_token

@pytest.fixture
def setup_test_data(db_session):
    # Create two businesses
    b1 = Business(legal_name="Test Business 1", gstin="22AAAAA0000A1Z5")
    b2 = Business(legal_name="Test Business 2")
    db_session.add(b1)
    db_session.add(b2)
    db_session.commit()
    
    # Create users
    pwd = hash_password("password")
    user_admin1 = User(
        email="admin1@b1.com", password_hash=pwd, role="admin",
        name="Admin One", is_active=True, business_id=b1.id
    )
    user_staff1 = User(
        email="staff1@b1.com", password_hash=pwd, role="staff",
        name="Staff One", is_active=True, business_id=b1.id
    )
    user_admin2 = User(
        email="admin2@b2.com", password_hash=pwd, role="admin",
        name="Admin Two", is_active=True, business_id=b2.id
    )
    db_session.add(user_admin1)
    db_session.add(user_staff1)
    db_session.add(user_admin2)
    db_session.commit()

    return {
        "b1": b1,
        "b2": b2,
        "admin1": user_admin1,
        "staff1": user_staff1,
        "admin2": user_admin2
    }

def get_auth_headers(user):
    token = create_access_token({"sub": str(user.id), "business_id": user.business_id, "role": user.role})
    return {"Authorization": f"Bearer {token}"}

def test_get_business_success(client, setup_test_data):
    admin1 = setup_test_data["admin1"]
    headers = get_auth_headers(admin1)
    
    resp = client.get("/api/business", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["legal_name"] == "Test Business 1"
    assert data["gstin"] == "22AAAAA0000A1Z5"
    assert data["id"] == setup_test_data["b1"].id

def test_get_business_unauthorized(client):
    resp = client.get("/api/business")
    assert resp.status_code == 401

def test_put_business_success(client, setup_test_data, db_session):
    admin1 = setup_test_data["admin1"]
    headers = get_auth_headers(admin1)
    
    update_payload = {
        "legal_name": "Updated Test Business 1",
        "trade_name": "New Trade Name",
        "pincode": "110001"
    }
    resp = client.put("/api/business", json=update_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["legal_name"] == "Updated Test Business 1"
    assert data["trade_name"] == "New Trade Name"
    assert data["pincode"] == "110001"
    
    # verify db
    b = db_session.query(Business).filter(Business.id == admin1.business_id).first()
    assert b.legal_name == "Updated Test Business 1"
    assert b.trade_name == "New Trade Name"

def test_put_business_isolation(client, setup_test_data, db_session):
    admin1 = setup_test_data["admin1"]
    b2 = setup_test_data["b2"]
    headers = get_auth_headers(admin1)
    
    update_payload = {
        "legal_name": "Should NOT change B2"
    }
    resp = client.put("/api/business", json=update_payload, headers=headers)
    assert resp.status_code == 200
    
    db_session.refresh(b2)
    assert b2.legal_name == "Test Business 2"  # B2 should remain untouched

def test_put_business_not_admin(client, setup_test_data):
    staff1 = setup_test_data["staff1"]
    headers = get_auth_headers(staff1)
    
    update_payload = {
        "legal_name": "Staff updated name"
    }
    resp = client.put("/api/business", json=update_payload, headers=headers)
    assert resp.status_code == 403
    assert "Not enough permissions" in resp.text
