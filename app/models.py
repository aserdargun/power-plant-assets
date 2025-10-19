from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

from .schemas import AssetStatus, WorkOrderPriority, WorkOrderStatus

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(UTC)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=False)
    status = Column(Enum(AssetStatus), nullable=False, default=AssetStatus.active)
    location = Column(String(100), nullable=False)
    capacity_mw = Column(Float, nullable=False)
    installed_at = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    work_orders = relationship(
        "WorkOrder",
        back_populates="asset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class WorkOrder(Base):
    __tablename__ = "work_orders"
    __table_args__ = (UniqueConstraint("asset_id", "title", name="uq_work_order_title"),)

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum(WorkOrderStatus), nullable=False, default=WorkOrderStatus.open
    )
    priority = Column(
        Enum(WorkOrderPriority), nullable=False, default=WorkOrderPriority.medium
    )
    scheduled_start = Column(Date, nullable=True)
    scheduled_end = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    asset = relationship("Asset", back_populates="work_orders")
