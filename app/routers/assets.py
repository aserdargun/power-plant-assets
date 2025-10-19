from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=List[schemas.AssetRead])
def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[schemas.AssetStatus] = Query(
        default=None, alias="status", description="Filter by asset status"
    ),
    search: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=100,
        description="Case-insensitive fuzzy search on asset name",
    ),
    db: Session = Depends(get_db),
) -> List[schemas.AssetRead]:
    assets = crud.list_assets(
        db, skip=skip, limit=limit, status_filter=status_filter, search=search
    )
    return assets


@router.post("", response_model=schemas.AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: schemas.AssetCreate, db: Session = Depends(get_db)) -> schemas.AssetRead:
    asset = crud.create_asset(db, payload)
    return asset


@router.get("/{asset_id}", response_model=schemas.AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)) -> schemas.AssetRead:
    asset = crud.get_asset_or_404(db, asset_id)
    return asset


@router.patch("/{asset_id}", response_model=schemas.AssetRead)
def update_asset(
    asset_id: int, payload: schemas.AssetUpdate, db: Session = Depends(get_db)
) -> schemas.AssetRead:
    asset = crud.get_asset_or_404(db, asset_id)
    updated_asset = crud.update_asset(db, asset, payload)
    return updated_asset


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> Response:
    asset = crud.get_asset_or_404(db, asset_id)
    crud.delete_asset(db, asset)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
