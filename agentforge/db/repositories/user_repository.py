"""
User Repository for Database Operations
"""
from typing import Sequence
from sqlalchemy.orm import Session
from agentforge.db.models import User


class UserRepository:
    """Repository handling CRUD operations for User entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        """Fetch user by primary key ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        """Fetch user by unique email address."""
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def create(self, email: str, hashed_password: str, role: str = "USER") -> User:
        """Create and persist a new user record."""
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            role=role.upper()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_role(self, user_id: str, new_role: str) -> User | None:
        """Update role for a user."""
        user = self.get_by_id(user_id)
        if user:
            user.role = new_role.upper()
            self.db.commit()
            self.db.refresh(user)
        return user

    def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[User]:
        """List users with pagination."""
        return self.db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
