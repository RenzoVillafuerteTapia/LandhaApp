# Ruta: backend/app/contexts/customers/interfaces/router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.contexts.customers.infrastructure.models import CustomerModel
from app.database import get_db
from app.shared.dependencies import get_current_user

router = APIRouter()


class CustomerCreate(BaseModel):
    name: str
    document_type: str = "DNI"
    document_number: Optional[str] = None
    business_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    document_type: str
    document_number: Optional[str] = None
    business_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    model_config = {"from_attributes": True}


@router.get("", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(CustomerModel).all()


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    customer = CustomerModel(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer