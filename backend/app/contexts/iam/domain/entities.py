# Ruta: backend/app/contexts/iam/domain/entities.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Role:
    id: Optional[int]
    name: str
    description: Optional[str] = None


@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    full_name: str
    hashed_password: str
    role_id: int
    role_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    def is_admin(self) -> bool:
        return self.role_name == "admin"

    def is_seller(self) -> bool:
        return self.role_name == "seller"