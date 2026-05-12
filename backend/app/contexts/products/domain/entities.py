# Ruta: backend/app/contexts/products/domain/entities.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: Optional[int]
    name: str
    description: Optional[str] = None


@dataclass
class Supplier:
    id: Optional[int]
    name: str
    ruc: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


@dataclass
class Product:
    id: Optional[int]
    code: str
    name: str
    unit: str
    price: float
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None
    is_active: bool = True