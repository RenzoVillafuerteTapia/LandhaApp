# Ruta: backend/app/contexts/billing/interfaces/router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.contexts.billing.application.use_cases import GetInvoiceUseCase, IssueInvoiceUseCase
from app.database import get_db
from app.shared.dependencies import require_role, get_current_user

router = APIRouter()


class IssueInvoiceRequest(BaseModel):
    sale_id: int
    document_type: str  # "boleta" | "factura"


@router.post("/issue", status_code=201)
def issue_invoice(
    payload: IssueInvoiceRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("seller", "admin")),
):
    return IssueInvoiceUseCase(db).execute(
        sale_id=payload.sale_id,
        document_type=payload.document_type,
    )


@router.get("/sale/{sale_id}")
def get_invoice_by_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return GetInvoiceUseCase(db).execute(sale_id=sale_id)