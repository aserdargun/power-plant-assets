from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/workorders", tags=["work orders"])


@router.get("", response_model=List[schemas.WorkOrderRead])
def list_work_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[schemas.WorkOrderStatus] = Query(
        default=None, alias="status", description="Filter by work order status"
    ),
    priority_filter: Optional[schemas.WorkOrderPriority] = Query(
        default=None, alias="priority", description="Filter by work order priority"
    ),
    asset_id: Optional[int] = Query(
        default=None,
        gt=0,
        description="Limit to work orders for a specific asset",
    ),
    db: Session = Depends(get_db),
) -> List[schemas.WorkOrderRead]:
    work_orders = crud.list_work_orders(
        db,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        priority_filter=priority_filter,
        asset_id=asset_id,
    )
    return work_orders


@router.post("", response_model=schemas.WorkOrderRead, status_code=status.HTTP_201_CREATED)
def create_work_order(
    payload: schemas.WorkOrderCreate, db: Session = Depends(get_db)
) -> schemas.WorkOrderRead:
    work_order = crud.create_work_order(db, payload)
    return work_order


@router.get("/{work_order_id}", response_model=schemas.WorkOrderRead)
def get_work_order(work_order_id: int, db: Session = Depends(get_db)) -> schemas.WorkOrderRead:
    work_order = crud.get_work_order_or_404(db, work_order_id)
    return work_order


@router.patch("/{work_order_id}", response_model=schemas.WorkOrderRead)
def update_work_order(
    work_order_id: int, payload: schemas.WorkOrderUpdate, db: Session = Depends(get_db)
) -> schemas.WorkOrderRead:
    work_order = crud.get_work_order_or_404(db, work_order_id)
    updated_work_order = crud.update_work_order(db, work_order, payload)
    return updated_work_order


@router.delete(
    "/{work_order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_work_order(work_order_id: int, db: Session = Depends(get_db)) -> Response:
    work_order = crud.get_work_order_or_404(db, work_order_id)
    crud.delete_work_order(db, work_order)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
