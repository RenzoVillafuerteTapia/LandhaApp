# Ruta: backend/app/contexts/inventory/infrastructure/models.py

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockLocationModel(Base):
    __tablename__ = "stock_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # "store" | "warehouse"

    stocks: Mapped[list["InventoryStockModel"]] = relationship(
        "InventoryStockModel", back_populates="location"
    )


class InventoryStockModel(Base):
    __tablename__ = "inventory_stock"
    __table_args__ = (UniqueConstraint("product_id", "location_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_locations.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    location: Mapped["StockLocationModel"] = relationship(
        "StockLocationModel", back_populates="stocks"
    )


class InventoryMovementModel(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_locations.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # "in" | "out" | "adjustment" | "transfer_in" | "transfer_out" | "sale"
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference: Mapped[str] = mapped_column(String(200), nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )