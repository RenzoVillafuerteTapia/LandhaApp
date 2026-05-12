# Ruta: backend/app/contexts/products/interfaces/schemas.py

from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    name: str
    ruc: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class SupplierResponse(BaseModel):
    id: int
    name: str
    ruc: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    unit: str = "UND"
    price: float
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None

class ProductUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    unit: str
    price: float
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    is_active: bool
    model_config = {"from_attributes": True}