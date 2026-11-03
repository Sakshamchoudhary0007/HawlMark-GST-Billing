"""
SQLAlchemy declarative base and timestamp mixin.

All models inherit from Base. Models that need automatic
created_at / updated_at columns mix in TimestampMixin.
"""

import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns to a model.

    Both columns store timezone-aware UTC datetimes.
    created_at is set automatically on INSERT.
    updated_at is set automatically on INSERT and UPDATE.
    """

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
