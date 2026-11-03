import pytest
from app.models.user import User

@pytest.fixture
def setup_users_auth(client, db_session):
    # Admin User A in Business A
    res_a = client.post("/api/auth/register", json={
        "business_name": "Business A",
        "name": "Admin A",
        "email": "admin.a@example.com",
        "password": "Password123!"
    })
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Admin User B in Business B
    res_b = client.post("/api/auth/register", json={
        "business_name": "Business B",
        "name": "Admin B",
        "email": "admin.b@example.com",
        "password": "Password123!"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    return headers_a, headers_b

def test_admin_create_user(client, setup_users_auth):
    headers_a, _ = setup_users_auth
    
    # Create Staff user
    payload = {
        "name": "Staff A",
        "email": "staff.a@example.com",
        "password": "Password123!",
        "role": "staff"
    }
    response = client.post("/api/users", json=payload, headers=headers_a)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Staff A"
    assert data["email"] == "staff.a@example.com"
    assert data["role"] == "staff"

def test_staff_cannot_create_user(client, setup_users_auth):
    headers_a, _ = setup_users_auth
    
    # Create Staff user
    payload = {
        "name": "Staff A",
        "email": "staff.a@example.com",
        "password": "Password123!",
        "role": "staff"
    }
    client.post("/api/users", json=payload, headers=headers_a)

    # Login as staff
    login_res = client.post("/api/auth/login", json={
        "email": "staff.a@example.com",
        "password": "Password123!"
    })
    staff_token = login_res.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # Staff tries to create user
    payload_2 = {
        "name": "Staff B",
        "email": "staff.b@example.com",
        "password": "Password123!",
        "role": "staff"
    }
    response = client.post("/api/users", json=payload_2, headers=staff_headers)
    assert response.status_code == 403

def test_business_isolation_for_users(client, setup_users_auth):
    headers_a, headers_b = setup_users_auth

    # Business A creates a user
    res_a = client.post("/api/users", json={
        "name": "Staff A",
        "email": "staff.iso@example.com",
        "password": "Password123!",
        "role": "staff"
    }, headers=headers_a)
    user_id = res_a.json()["id"]

    # Business B lists users
    res_b = client.get("/api/users", headers=headers_b)
    assert res_b.status_code == 200
    b_users = res_b.json()["items"]
    assert len(b_users) == 1
    assert b_users[0]["email"] == "admin.b@example.com"

    # Business B tries to update Business A's user role
    res_b_patch = client.patch(f"/api/users/{user_id}/role", json={"role": "admin"}, headers=headers_b)
    assert res_b_patch.status_code == 404

def test_user_status_and_role_update(client, setup_users_auth):
    headers_a, _ = setup_users_auth
    
    # Create Staff user
    res = client.post("/api/users", json={
        "name": "Staff A",
        "email": "staff.update@example.com",
        "password": "Password123!",
        "role": "staff"
    }, headers=headers_a)
    user_id = res.json()["id"]

    # Update role
    res_role = client.patch(f"/api/users/{user_id}/role", json={"role": "admin"}, headers=headers_a)
    assert res_role.status_code == 200
    assert res_role.json()["role"] == "admin"

    # Update status
    res_status = client.patch(f"/api/users/{user_id}/status", json={"is_active": False}, headers=headers_a)
    assert res_status.status_code == 200
    assert res_status.json()["is_active"] == False

    # Try to login with inactive user
    login_res = client.post("/api/auth/login", json={
        "email": "staff.update@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 401
