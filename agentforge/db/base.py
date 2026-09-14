"""
Base Declarative Model and Utility Mixins for SQLAlchemy 2.x
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase


def generate_uuid() -> str:
    """Generate a standard string UUID primary key."""
    return str(uuid.uuid4())


def current_utc() -> datetime:
    """Return timezone-aware UTC current timestamp."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""
    pass


class TimestampMixin:
    """Mixin for tracking creation and update timestamps."""
    created_at = Column(DateTime(timezone=True), default=current_utc, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=current_utc, onupdate=current_utc, nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key generation."""
    id = Column(String(36), primary_key=True, default=generate_uuid)
