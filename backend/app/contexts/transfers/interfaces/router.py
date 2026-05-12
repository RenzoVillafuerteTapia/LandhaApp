# Ruta: backend/app/contexts/transfers/interfaces/router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.contexts.transfers.application.use_cases import (
    CreateTransferUseCase, ListTransfersUseCase, TransferItem,
)
from app.database import get_db
from app.shared.dependencies import get_current_user, require_admin

router = APIRouter()


class TransferItemRequest(BaseModel):
    product_id: int
    quantity: int


class CreateTransferRequest(BaseModel):
    origin_id: int
    destination_id: int
    items: List[TransferItemRequest]
    notes: Optional[str] = None


@router.post("", status_code=201)
def create_transfer(
    payload: CreateTransferRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    items = [TransferItem(product_id=i.product_id, quantity=i.quantity) for i in payload.items]
    return CreateTransferUseCase(db).execute(
        origin_id=payload.origin_id,
        destination_id=payload.destination_id,
        user_id=int(current_user["sub"]),
        items=items,
        notes=payload.notes,
    )


@router.get("")
def list_transfers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ListTransfersUseCase(db).execute()