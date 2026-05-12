# Ruta: backend/app/contexts/inventory/interfaces/router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.contexts.inventory.application.use_cases import AdjustStockUseCase, GetStockUseCase
from app.contexts.inventory.infrastructure.models import StockLocationModel
from app.database import get_db
from app.shared.dependencies import get_current_user, require_admin

router = APIRouter()


class AdjustStockRequest(BaseModel):
    product_id: int
    location_id: int
    quantity: int
    movement_type: str  # "in" | "out"
    notes: Optional[str] = None


class LocationCreate(BaseModel):
    name: str
    type: str  # "store" | "warehouse"


@router.get("/stock")
def get_stock(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return GetStockUseCase(db).execute(location_id=location_id)


@router.post("/stock/adjust")
def adjust_stock(
    payload: AdjustStockRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return AdjustStockUseCase(db).execute(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        movement_type=payload.movement_type,
        user_id=int(current_user["sub"]),
        notes=payload.notes,
    )


@router.get("/locations")
def list_locations(db: Session = Depends(get_db), _=Depends(get_current_user)):
    locations = db.query(StockLocationModel).all()
    return [{"id": l.id, "name": l.name, "type": l.type} for l in locations]


@router.post("/locations", status_code=201)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    loc = StockLocationModel(name=payload.name, type=payload.type)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return {"id": loc.id, "name": loc.name, "type": loc.type}