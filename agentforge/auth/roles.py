"""
Role-Based Access Control (RBAC) Classifications for AgentForge AI
"""
from enum import Enum


class UserRole(str, Enum):
    """Platform User Roles"""
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    USER = "USER"
    VIEWER = "VIEWER"


ROLE_HIERARCHY = {
    UserRole.ADMIN: 4,
    UserRole.ENGINEER: 3,
    UserRole.USER: 2,
    UserRole.VIEWER: 1,
}


def has_sufficient_role(user_role: str, required_role: UserRole) -> bool:
    """Check if user_role satisfies required_role hierarchy level."""
    try:
        user_level = ROLE_HIERARCHY.get(UserRole(user_role.upper()), 0)
        req_level = ROLE_HIERARCHY.get(required_role, 4)
        return user_level >= req_level
    except ValueError:
        return False
