# Ruta: backend/app/contexts/transfers/infrastructure/models.py

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StockTransferModel(Base):
    __tablename__ = "stock_transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    origin_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_locations.id"), nullable=False)
    destination_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_locations.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    details: Mapped[list["StockTransferDetailModel"]] = relationship(
        "StockTransferDetailModel", back_populates="transfer", cascade="all, delete-orphan"
    )


class StockTransferDetailModel(Base):
    __tablename__ = "stock_transfer_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transfer_id: Mapped[int] = mapped_column(Integer, ForeignKey("stock_transfers.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    transfer: Mapped["StockTransferModel"] = relationship(
        "StockTransferModel", back_populates="details"
    )