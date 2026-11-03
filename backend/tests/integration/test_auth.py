"""Integration tests for Authentication API endpoints."""

import pytest
from app.models.user import User
from app.models.business import Business
from app.auth.password import hash_password, verify_password


class TestAuthAPI:
    """Test auth routes: register, login, refresh, me, logout."""

    def test_register_user_success(self, client):
        payload = {
            "business_name": "Test Acme Corp",
            "name": "John Admin",
            "email": "john.admin@example.com",
            "password": "SecurePassword123!"
        }
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email_conflict(self, client):
        payload = {
            "business_name": "Business One",
            "name": "Owner One",
            "email": "dup.owner@example.com",
            "password": "Password123!"
        }
        res1 = client.post("/api/auth/register", json=payload)
        assert res1.status_code == 200

        # Attempt to register again with same email
        payload2 = {
            "business_name": "Business Two",
            "name": "Owner Two",
            "email": "dup.owner@example.com",
            "password": "Password123!"
        }
        res2 = client.post("/api/auth/register", json=payload2)
        assert res2.status_code == 409
        err = res2.json()
        assert err["error"]["code"] == "CONFLICT"

    def test_login_success_and_me(self, client):
        reg_payload = {
            "business_name": "Login Test Ltd",
            "name": "Jane User",
            "email": "jane.user@example.com",
            "password": "Password123!"
        }
        client.post("/api/auth/register", json=reg_payload)

        # Login
        login_payload = {
            "email": "jane.user@example.com",
            "password": "Password123!"
        }
        login_res = client.post("/api/auth/login", json=login_payload)
        assert login_res.status_code == 200
        tokens = login_res.json()
        access_token = tokens["access_token"]

        # Call GET /api/auth/me
        headers = {"Authorization": f"Bearer {access_token}"}
        me_res = client.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        user_info = me_res.json()
        assert user_info["email"] == "jane.user@example.com"
        assert user_info["name"] == "Jane User"
        assert user_info["role"] == "admin"
        assert user_info["is_active"] is True
        assert "business_id" in user_info

    def test_login_invalid_password(self, client):
        reg_payload = {
            "business_name": "Wrong Pass Co",
            "name": "Alice",
            "email": "alice@example.com",
            "password": "CorrectPassword123!"
        }
        client.post("/api/auth/register", json=reg_payload)

        # Attempt login with wrong password
        login_payload = {
            "email": "alice@example.com",
            "password": "WrongPassword123!"
        }
        login_res = client.post("/api/auth/login", json=login_payload)
        assert login_res.status_code == 401
        err = login_res.json()
        assert err["error"]["code"] == "AUTHENTICATION_ERROR"

    def test_refresh_token(self, client):
        reg_payload = {
            "business_name": "Refresh Co",
            "name": "Bob",
            "email": "bob@example.com",
            "password": "Password123!"
        }
        reg_res = client.post("/api/auth/register", json=reg_payload)
        refresh_token = reg_res.json()["refresh_token"]

        refresh_res = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_res.status_code == 200
        new_tokens = refresh_res.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

    def test_me_unauthorized_without_token(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401

    def test_me_unauthorized_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 401
