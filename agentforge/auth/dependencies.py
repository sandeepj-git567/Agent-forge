"""
FastAPI Authentication Dependencies and RBAC Security Guards
"""
from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from agentforge.auth.jwt import decode_access_token
from agentforge.auth.roles import UserRole, has_sufficient_role
from agentforge.db.models import User
from agentforge.db.repositories.user_repository import UserRepository
from agentforge.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to extract and authenticate current user from Bearer JWT token.
    Raises HTTP 401 Unauthorized if missing, expired, or invalid.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing. Bearer JWT required in Authorization header.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        user_id: str | None = payload.get("user_id")
        if not email and not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims: missing subject or user_id.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {err!s}",
            headers={"WWW-Authenticate": "Bearer"}
        ) from err

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id) if user_id else None
    if not user and email:
        user = user_repo.get_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account specified in authentication token does not exist.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    return user


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User | None:
    """
    FastAPI dependency to optionally extract authenticated user if Bearer token is provided.
    Returns None if token is absent or invalid without raising 401 error.
    """
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except HTTPException:
        return None


def require_role(required_role: UserRole) -> Callable[..., User]:
    """
    Factory dependency enforcing minimum Role-Based Access Control (RBAC) role level.
    Raises HTTP 403 Forbidden if user's role hierarchy rank is below required_role.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_sufficient_role(current_user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Operation requires minimum role '{required_role.value}', but current role is '{current_user.role}'."
            )
        return current_user

    return role_checker
