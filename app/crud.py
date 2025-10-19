from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from . import models, schemas


# Asset CRUD helpers -----------------------------------------------------------------
def get_asset_or_404(db: Session, asset_id: int) -> models.Asset:
    asset = db.get(models.Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


def get_asset_by_name(db: Session, name: str) -> Optional[models.Asset]:
    stmt = select(models.Asset).where(func.lower(models.Asset.name) == name.lower())
    return db.execute(stmt).scalar_one_or_none()


def list_assets(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[schemas.AssetStatus] = None,
    search: Optional[str] = None,
) -> Iterable[models.Asset]:
    stmt: Select[tuple[models.Asset]] = select(models.Asset).options(
        joinedload(models.Asset.work_orders)
    )
    if status_filter:
        stmt = stmt.where(models.Asset.status == status_filter)
    if search:
        search_like = f"%{search.lower()}%"
        stmt = stmt.where(func.lower(models.Asset.name).like(search_like))
    stmt = stmt.order_by(models.Asset.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).unique().scalars().all()


def create_asset(db: Session, payload: schemas.AssetCreate) -> models.Asset:
    if get_asset_by_name(db, payload.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Asset with this name already exists",
        )
    asset = models.Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(db: Session, asset: models.Asset, payload: schemas.AssetUpdate) -> models.Asset:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    asset.updated_at = datetime.now(UTC)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset: models.Asset) -> None:
    db.delete(asset)
    db.commit()


# Work order CRUD helpers -------------------------------------------------------------
def list_work_orders(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[schemas.WorkOrderStatus] = None,
    priority_filter: Optional[schemas.WorkOrderPriority] = None,
    asset_id: Optional[int] = None,
) -> Iterable[models.WorkOrder]:
    stmt: Select[tuple[models.WorkOrder]] = select(models.WorkOrder).options(
        joinedload(models.WorkOrder.asset)
    )
    if status_filter:
        stmt = stmt.where(models.WorkOrder.status == status_filter)
    if priority_filter:
        stmt = stmt.where(models.WorkOrder.priority == priority_filter)
    if asset_id:
        stmt = stmt.where(models.WorkOrder.asset_id == asset_id)
    stmt = stmt.order_by(models.WorkOrder.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).unique().scalars().all()


def get_work_order_or_404(db: Session, work_order_id: int) -> models.WorkOrder:
    work_order = db.get(models.WorkOrder, work_order_id)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


def create_work_order(db: Session, payload: schemas.WorkOrderCreate) -> models.WorkOrder:
    asset = db.get(models.Asset, payload.asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Related asset not found",
        )
    work_order = models.WorkOrder(**payload.model_dump())
    db.add(work_order)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Work order with this title already exists for the asset",
        ) from exc
    db.refresh(work_order)
    return work_order


def update_work_order(
    db: Session, work_order: models.WorkOrder, payload: schemas.WorkOrderUpdate
) -> models.WorkOrder:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(work_order, field, value)
    work_order.updated_at = datetime.now(UTC)
    db.add(work_order)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Work order with this title already exists for the asset",
        ) from exc
    db.refresh(work_order)
    return work_order


def delete_work_order(db: Session, work_order: models.WorkOrder) -> None:
    db.delete(work_order)
    db.commit()
