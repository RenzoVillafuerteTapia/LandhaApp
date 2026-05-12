# Ruta: backend/app/contexts/sales/interfaces/router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.contexts.sales.application.use_cases import (
    CreateSaleUseCase, ListSalesUseCase, SaleItem,
)
from app.database import get_db
from app.shared.dependencies import get_current_user, require_role

router = APIRouter()


class SaleItemRequest(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class CreateSaleRequest(BaseModel):
    location_id: int
    items: List[SaleItemRequest]
    payment_method: str = "cash"
    customer_id: Optional[int] = None


@router.post("", status_code=201)
def create_sale(
    payload: CreateSaleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("seller", "admin")),
):
    items = [SaleItem(product_id=i.product_id, quantity=i.quantity, unit_price=i.unit_price)
             for i in payload.items]
    return CreateSaleUseCase(db).execute(
        user_id=int(current_user["sub"]),
        location_id=payload.location_id,
        items=items,
        payment_method=payload.payment_method,
        customer_id=payload.customer_id,
    )


@router.get("")
def list_sales(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ListSalesUseCase(db).execute()