# Ruta: backend/app/contexts/iam/domain/repositories.py

from abc import ABC, abstractmethod
from typing import Optional

from app.contexts.iam.domain.entities import Role, User


class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]: ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def find_all(self) -> list[User]: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def update(self, user: User) -> User: ...

    @abstractmethod
    def delete(self, user_id: int) -> None: ...


class RoleRepository(ABC):
    @abstractmethod
    def find_by_id(self, role_id: int) -> Optional[Role]: ...

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Role]: ...

    @abstractmethod
    def find_all(self) -> list[Role]: ...

    @abstractmethod
    def save(self, role: Role) -> Role: ...