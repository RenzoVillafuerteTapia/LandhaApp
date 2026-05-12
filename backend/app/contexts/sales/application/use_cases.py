# Ruta: backend/app/contexts/sales/application/use_cases.py

from dataclasses import dataclass
from typing import List, Optional
from sqlalchemy.orm import Session

from app.contexts.inventory.application.use_cases import _ensure_stock, register_movement
from app.contexts.inventory.infrastructure.models import InventoryStockModel
from app.contexts.sales.infrastructure.models import SaleDetailModel, SaleModel
from app.shared.exceptions import BusinessRuleViolation, EntityNotFound, InsufficientStock


@dataclass
class SaleItem:
    product_id: int
    quantity: int
    unit_price: float


class CreateSaleUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self,
        user_id: int,
        location_id: int,
        items: List[SaleItem],
        payment_method: str = "cash",
        customer_id: Optional[int] = None,
    ) -> dict:
        if not items:
            raise BusinessRuleViolation("La venta debe contener al menos un producto.")

        # Validar stock para todos los items
        for item in items:
            stock = self.db.query(InventoryStockModel).filter(
                InventoryStockModel.product_id == item.product_id,
                InventoryStockModel.location_id == location_id,
            ).first()
            available = stock.quantity if stock else 0
            if available < item.quantity:
                raise InsufficientStock(f"producto_id:{item.product_id}", available, item.quantity)

        subtotal = sum(i.quantity * i.unit_price for i in items)
        tax = round(subtotal * 0.18, 2)
        total = round(subtotal + tax, 2)

        sale = SaleModel(
            user_id=user_id,
            location_id=location_id,
            customer_id=customer_id,
            subtotal=subtotal,
            tax=tax,
            total=total,
            payment_method=payment_method,
            status="completed",
        )
        self.db.add(sale)
        self.db.flush()

        for item in items:
            detail = SaleDetailModel(
                sale_id=sale.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=round(item.quantity * item.unit_price, 2),
            )
            self.db.add(detail)

            # Descontar stock
            stock = _ensure_stock(self.db, item.product_id, location_id)
            stock.quantity -= item.quantity

            # Registrar movimiento
            register_movement(
                self.db, item.product_id, location_id, user_id,
                "sale", item.quantity, reference=f"sale:{sale.id}",
            )

        self.db.commit()
        return {
            "sale_id": sale.id,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "status": "completed",
        }


class ListSalesUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self) -> list:
        sales = self.db.query(SaleModel).order_by(SaleModel.created_at.desc()).all()
        result = []
        for s in sales:
            result.append({
                "id": s.id,
                "customer_id": s.customer_id,
                "user_id": s.user_id,
                "location_id": s.location_id,
                "subtotal": float(s.subtotal),
                "tax": float(s.tax),
                "total": float(s.total),
                "payment_method": s.payment_method,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "details": [
                    {
                        "product_id": d.product_id,
                        "quantity": d.quantity,
                        "unit_price": float(d.unit_price),
                        "subtotal": float(d.subtotal),
                    }
                    for d in s.details
                ],
            })
        return result