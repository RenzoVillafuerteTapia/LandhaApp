# Ruta: backend/app/contexts/inventory/application/use_cases.py

from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.contexts.inventory.infrastructure.models import (
    InventoryMovementModel, InventoryStockModel, StockLocationModel,
)
from app.shared.exceptions import BusinessRuleViolation, EntityNotFound, InsufficientStock


@dataclass
class StockEntry:
    product_id: int
    location_id: int
    quantity: int


class GetStockUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, location_id: int = None) -> list[dict]:
        q = self.db.query(InventoryStockModel)
        if location_id:
            q = q.filter(InventoryStockModel.location_id == location_id)
        return [
            {
                "product_id": s.product_id,
                "location_id": s.location_id,
                "location_name": s.location.name if s.location else None,
                "quantity": s.quantity,
            }
            for s in q.all()
        ]


class AdjustStockUseCase:
    """Permite ajuste manual de stock (entrada o salida directa). Solo admin."""

    def __init__(self, db: Session):
        self.db = db

    def execute(
        self, product_id: int, location_id: int, quantity: int,
        movement_type: str, user_id: int, notes: str = None,
    ) -> dict:
        location = self.db.query(StockLocationModel).filter(
            StockLocationModel.id == location_id
        ).first()
        if not location:
            raise EntityNotFound("Ubicación", location_id)

        stock = self.db.query(InventoryStockModel).filter(
            InventoryStockModel.product_id == product_id,
            InventoryStockModel.location_id == location_id,
        ).first()

        if not stock:
            stock = InventoryStockModel(
                product_id=product_id, location_id=location_id, quantity=0
            )
            self.db.add(stock)
            self.db.flush()

        if movement_type == "out" and stock.quantity < quantity:
            raise InsufficientStock("producto", stock.quantity, quantity)

        stock.quantity = stock.quantity + quantity if movement_type == "in" else stock.quantity - quantity

        movement = InventoryMovementModel(
            product_id=product_id, location_id=location_id,
            user_id=user_id, movement_type=movement_type,
            quantity=quantity, notes=notes, reference="manual_adjustment",
        )
        self.db.add(movement)
        self.db.commit()
        return {"product_id": product_id, "location_id": location_id, "new_quantity": stock.quantity}


def _ensure_stock(db: Session, product_id: int, location_id: int) -> InventoryStockModel:
    """Helper: obtiene o crea el registro de stock para producto+ubicación."""
    stock = db.query(InventoryStockModel).filter(
        InventoryStockModel.product_id == product_id,
        InventoryStockModel.location_id == location_id,
    ).first()
    if not stock:
        stock = InventoryStockModel(product_id=product_id, location_id=location_id, quantity=0)
        db.add(stock)
        db.flush()
    return stock


def register_movement(
    db: Session, product_id: int, location_id: int, user_id: int,
    movement_type: str, quantity: int, reference: str = None, notes: str = None,
) -> None:
    """Helper reutilizable para registrar movimientos desde otros contextos."""
    movement = InventoryMovementModel(
        product_id=product_id, location_id=location_id,
        user_id=user_id, movement_type=movement_type,
        quantity=quantity, reference=reference, notes=notes,
    )
    db.add(movement)