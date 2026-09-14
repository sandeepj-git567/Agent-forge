"""
Comprehensive Unit Tests for Database Authentication and RBAC (Stage 6)
"""
import pytest
from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient

from agentforge.api.main import app
from agentforge.auth.dependencies import get_current_user, require_role
from agentforge.auth.roles import UserRole
from agentforge.db.models import User

client = TestClient(app)


# Temporary route added for RBAC testing
rbac_test_app = FastAPI()

@rbac_test_app.get("/admin-only")
def admin_only_endpoint(user: User = Depends(require_role(UserRole.ADMIN))):
    return {"status": "success", "admin": user.email}

rbac_client = TestClient(rbac_test_app)


def test_user_registration_and_duplicate_check():
    payload = {
        "email": "stage6_user@agentforge.ai",
        "password": "SecurePassword123!",
        "role": "USER"
    }

    # 1. Register new user
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["status"] == "success"
    assert "access_token" in data
    assert data["user"]["email"] == "stage6_user@agentforge.ai"
    assert data["user"]["role"] == "USER"

    # 2. Duplicate registration attempt must fail
    dup_res = client.post("/api/v1/auth/register", json=payload)
    assert dup_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in dup_res.json()["detail"].lower()


def test_user_login_and_me_endpoint():
    email = "login_test@agentforge.ai"
    password = "MySecretPassword123!"

    # Register first
    client.post("/api/v1/auth/register", json={"email": email, "password": password})

    # Invalid password login
    bad_login = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword!"})
    assert bad_login.status_code == status.HTTP_401_UNAUTHORIZED

    # Valid login
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == status.HTTP_200_OK
    token = login_res.json()["access_token"]
    assert token is not None

    # Call /auth/me without token -> 401
    me_unauth = client.get("/api/v1/auth/me")
    assert me_unauth.status_code == status.HTTP_401_UNAUTHORIZED

    # Call /auth/me with Bearer token -> 200
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == status.HTTP_200_OK
    assert me_res.json()["email"] == email
    assert me_res.json()["role"] == "USER"


def test_change_password_and_logout():
    email = "changepw@agentforge.ai"
    old_pw = "OldPassword123!"
    new_pw = "NewPassword456!"

    # Register
    reg_res = client.post("/api/v1/auth/register", json={"email": email, "password": old_pw})
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Change password
    change_res = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": old_pw, "new_password": new_pw},
        headers=headers
    )
    assert change_res.status_code == status.HTTP_200_OK
    assert change_res.json()["status"] == "success"

    # Login with old password should now fail
    old_login = client.post("/api/v1/auth/login", json={"email": email, "password": old_pw})
    assert old_login.status_code == status.HTTP_401_UNAUTHORIZED

    # Login with new password should succeed
    new_login = client.post("/api/v1/auth/login", json={"email": email, "password": new_pw})
    assert new_login.status_code == status.HTTP_200_OK

    # Logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == status.HTTP_200_OK
    assert "logged out" in logout_res.json()["message"].lower()


def test_rbac_role_hierarchy_protection():
    # Register regular USER
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": "regular_user@agentforge.ai", "password": "UserPass123!", "role": "USER"}
    )
    user_token = reg_res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Register ADMIN user
    admin_reg = client.post(
        "/api/v1/auth/register",
        json={"email": "admin_user@agentforge.ai", "password": "AdminPass123!", "role": "ADMIN"}
    )
    admin_token = admin_reg.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Test protected route with USER token (must fail with 403 Forbidden)
    res_user = rbac_client.get("/admin-only", headers=user_headers)
    assert res_user.status_code == status.HTTP_403_FORBIDDEN
    assert "Access denied" in res_user.json()["detail"]

    # Test protected route with ADMIN token (must succeed with 200 OK)
    res_admin = rbac_client.get("/admin-only", headers=admin_headers)
    assert res_admin.status_code == status.HTTP_200_OK
    assert res_admin.json()["admin"] == "admin_user@agentforge.ai"
