# Ruta: backend/app/contexts/transfers/application/use_cases.py

from dataclasses import dataclass
from typing import List
from sqlalchemy.orm import Session

from app.contexts.inventory.application.use_cases import _ensure_stock, register_movement
from app.contexts.inventory.infrastructure.models import InventoryStockModel, StockLocationModel
from app.contexts.transfers.infrastructure.models import (
    StockTransferDetailModel, StockTransferModel,
)
from app.shared.exceptions import BusinessRuleViolation, EntityNotFound, InsufficientStock


@dataclass
class TransferItem:
    product_id: int
    quantity: int


class CreateTransferUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self,
        origin_id: int,
        destination_id: int,
        user_id: int,
        items: List[TransferItem],
        notes: str = None,
    ) -> dict:
        origin = self.db.query(StockLocationModel).filter(StockLocationModel.id == origin_id).first()
        if not origin:
            raise EntityNotFound("Ubicación origen", origin_id)

        destination = self.db.query(StockLocationModel).filter(
            StockLocationModel.id == destination_id
        ).first()
        if not destination:
            raise EntityNotFound("Ubicación destino", destination_id)

        if origin_id == destination_id:
            raise BusinessRuleViolation("El origen y destino deben ser distintos.")

        if not items:
            raise BusinessRuleViolation("La transferencia debe incluir al menos un producto.")

        # Validar stock en origen antes de ejecutar
        for item in items:
            stock = self.db.query(InventoryStockModel).filter(
                InventoryStockModel.product_id == item.product_id,
                InventoryStockModel.location_id == origin_id,
            ).first()
            available = stock.quantity if stock else 0
            if available < item.quantity:
                raise InsufficientStock(f"producto_id:{item.product_id}", available, item.quantity)

        # Crear la transferencia
        transfer = StockTransferModel(
            origin_id=origin_id,
            destination_id=destination_id,
            user_id=user_id,
            notes=notes,
            status="completed",
        )
        self.db.add(transfer)
        self.db.flush()

        # Mover stock y registrar movimientos
        for item in items:
            origin_stock = _ensure_stock(self.db, item.product_id, origin_id)
            origin_stock.quantity -= item.quantity

            dest_stock = _ensure_stock(self.db, item.product_id, destination_id)
            dest_stock.quantity += item.quantity

            detail = StockTransferDetailModel(
                transfer_id=transfer.id,
                product_id=item.product_id,
                quantity=item.quantity,
            )
            self.db.add(detail)

            register_movement(self.db, item.product_id, origin_id, user_id,
                              "transfer_out", item.quantity, reference=f"transfer:{transfer.id}")
            register_movement(self.db, item.product_id, destination_id, user_id,
                              "transfer_in", item.quantity, reference=f"transfer:{transfer.id}")

        self.db.commit()
        return {
            "transfer_id": transfer.id,
            "origin": origin.name,
            "destination": destination.name,
            "items_count": len(items),
            "status": "completed",
        }


class ListTransfersUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self) -> list:
        transfers = self.db.query(StockTransferModel).order_by(
            StockTransferModel.created_at.desc()
        ).all()
        result = []
        for t in transfers:
            result.append({
                "id": t.id,
                "origin_id": t.origin_id,
                "destination_id": t.destination_id,
                "user_id": t.user_id,
                "status": t.status,
                "notes": t.notes,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "details": [
                    {"product_id": d.product_id, "quantity": d.quantity}
                    for d in t.details
                ],
            })
        return result