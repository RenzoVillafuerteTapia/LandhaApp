# Ruta: backend/app/contexts/billing/application/use_cases.py

from sqlalchemy.orm import Session
from app.contexts.billing.infrastructure.models import InvoiceModel
from app.contexts.sales.infrastructure.models import SaleModel
from app.shared.exceptions import BusinessRuleViolation, EntityNotFound


class IssueInvoiceUseCase:
    SERIES = {"boleta": "B001", "factura": "F001"}

    def __init__(self, db: Session):
        self.db = db

    def execute(
        self, sale_id: int, document_type: str,
        validate_ruc: bool = False,
    ) -> dict:
        if document_type not in ("boleta", "factura"):
            raise BusinessRuleViolation("Tipo de documento inválido. Use 'boleta' o 'factura'.")

        sale = self.db.query(SaleModel).filter(SaleModel.id == sale_id).first()
        if not sale:
            raise EntityNotFound("Venta", sale_id)

        existing = self.db.query(InvoiceModel).filter(InvoiceModel.sale_id == sale_id).first()
        if existing:
            raise BusinessRuleViolation("Esta venta ya tiene un comprobante emitido.")

        series = self.SERIES[document_type]
        last = (
            self.db.query(InvoiceModel)
            .filter(InvoiceModel.series == series)
            .order_by(InvoiceModel.correlative.desc())
            .first()
        )
        correlative = (last.correlative + 1) if last else 1

        invoice = InvoiceModel(
            sale_id=sale_id,
            document_type=document_type,
            series=series,
            correlative=correlative,
            status="issued",
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        return {
            "invoice_id": invoice.id,
            "sale_id": sale_id,
            "document_type": document_type,
            "number": f"{series}-{str(correlative).zfill(8)}",
            "status": "issued",
            "issued_at": invoice.issued_at.isoformat(),
        }


class GetInvoiceUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, sale_id: int) -> dict:
        invoice = self.db.query(InvoiceModel).filter(InvoiceModel.sale_id == sale_id).first()
        if not invoice:
            raise EntityNotFound("Comprobante para venta", sale_id)
        return {
            "invoice_id": invoice.id,
            "sale_id": invoice.sale_id,
            "document_type": invoice.document_type,
            "number": f"{invoice.series}-{str(invoice.correlative).zfill(8)}",
            "status": invoice.status,
            "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
        }