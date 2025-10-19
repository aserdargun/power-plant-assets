from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class AssetStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    decommissioned = "decommissioned"


class WorkOrderStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class WorkOrderPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AssetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Unique asset name")
    category: str = Field(..., min_length=2, max_length=50, description="Asset category, e.g., turbine")
    status: AssetStatus = Field(default=AssetStatus.active)
    location: str = Field(..., min_length=2, max_length=100)
    capacity_mw: float = Field(..., gt=0, description="Installed capacity in megawatts")
    installed_at: date = Field(..., description="Commissioning date")

    model_config = {"extra": "forbid"}


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    status: Optional[AssetStatus] = None
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    capacity_mw: Optional[float] = Field(None, gt=0)
    installed_at: Optional[date] = None

    model_config = {"extra": "forbid"}


class WorkOrderSummary(BaseModel):
    id: int
    title: str
    status: WorkOrderStatus
    priority: WorkOrderPriority

    model_config = {"from_attributes": True}


class AssetRead(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    work_orders: List[WorkOrderSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class WorkOrderBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=10_000)
    status: WorkOrderStatus = Field(default=WorkOrderStatus.open)
    priority: WorkOrderPriority = Field(default=WorkOrderPriority.medium)
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    completed_at: Optional[datetime] = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_temporal_fields(cls, values: "WorkOrderBase") -> "WorkOrderBase":
        if (
            values.scheduled_end is not None
            and values.scheduled_start is not None
            and values.scheduled_end < values.scheduled_start
        ):
            raise ValueError("scheduled_end cannot be before scheduled_start")
        if (
            values.completed_at is not None
            and values.scheduled_start is not None
            and values.completed_at.date() < values.scheduled_start
        ):
            raise ValueError("completed_at cannot be before scheduled_start")
        return values


class WorkOrderCreate(WorkOrderBase):
    asset_id: int = Field(..., gt=0)


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = Field(None, max_length=10_000)
    status: Optional[WorkOrderStatus] = None
    priority: Optional[WorkOrderPriority] = None
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    completed_at: Optional[datetime] = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_temporal_fields(cls, values: "WorkOrderUpdate") -> "WorkOrderUpdate":
        if (
            values.scheduled_end is not None
            and values.scheduled_start is not None
            and values.scheduled_end < values.scheduled_start
        ):
            raise ValueError("scheduled_end cannot be before scheduled_start")
        if (
            values.completed_at is not None
            and values.scheduled_start is not None
            and values.completed_at.date() < values.scheduled_start
        ):
            raise ValueError("completed_at cannot be before scheduled_start")
        return values


class WorkOrderRead(WorkOrderBase):
    id: int
    asset_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
