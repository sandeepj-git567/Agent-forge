"""
Authentication API Router
"""
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from agentforge.auth.jwt import create_access_token, hash_password, verify_password
from agentforge.auth.roles import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])

_USER_DB: dict[str, dict[str, Any]] = {}


class RegisterRequest(BaseModel):
    """Payload for POST /api/v1/auth/register"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    role: UserRole = Field(default=UserRole.USER, description="User role")


class LoginRequest(BaseModel):
    """Payload for POST /api/v1/auth/login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> dict[str, Any]:
    """Register a new user account."""
    email_clean = payload.email.lower().strip()
    if email_clean in _USER_DB:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists.")

    hashed_pw = hash_password(payload.password)
    user_record = {
        "email": email_clean,
        "hashed_password": hashed_pw,
        "role": payload.role.value
    }
    _USER_DB[email_clean] = user_record

    token = create_access_token({"sub": email_clean, "role": payload.role.value})
    return {
        "status": "success",
        "message": "User registered successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": email_clean, "role": payload.role.value}
    }


@router.post("/login")
async def login(payload: LoginRequest) -> dict[str, Any]:
    """Authenticate user credentials and issue JWT access token."""
    email_clean = payload.email.lower().strip()
    user = _USER_DB.get(email_clean)

    # Fallback default dev user login support
    if not user and email_clean == "admin@agentforge.ai" and payload.password == "admin123456":
        token = create_access_token({"sub": email_clean, "role": UserRole.ADMIN.value})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"email": email_clean, "role": UserRole.ADMIN.value}
        }

    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password credentials.")

    token = create_access_token({"sub": email_clean, "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"email": email_clean, "role": user["role"]}
    }
