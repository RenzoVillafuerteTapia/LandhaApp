# Ruta: backend/app/contexts/iam/infrastructure/repositories.py

from typing import Optional

from sqlalchemy.orm import Session

from app.contexts.iam.domain.entities import Role, User
from app.contexts.iam.domain.repositories import RoleRepository, UserRepository
from app.contexts.iam.infrastructure.models import RoleModel, UserModel


def _model_to_user(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        full_name=model.full_name,
        hashed_password=model.hashed_password,
        role_id=model.role_id,
        role_name=model.role.name if model.role else None,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def _model_to_role(model: RoleModel) -> Role:
    return Role(id=model.id, name=model.name, description=model.description)


class SqlUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, user_id: int) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return _model_to_user(model) if model else None

    def find_by_username(self, username: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return _model_to_user(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return _model_to_user(model) if model else None

    def find_all(self) -> list[User]:
        models = self.db.query(UserModel).all()
        return [_model_to_user(m) for m in models]

    def save(self, user: User) -> User:
        model = UserModel(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            role_id=user.role_id,
            is_active=user.is_active,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_user(model)

    def update(self, user: User) -> User:
        model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError("Usuario no encontrado.")
        model.username = user.username
        model.email = user.email
        model.full_name = user.full_name
        model.hashed_password = user.hashed_password
        model.role_id = user.role_id
        model.is_active = user.is_active
        self.db.commit()
        self.db.refresh(model)
        return _model_to_user(model)

    def delete(self, user_id: int) -> None:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()


class SqlRoleRepository(RoleRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, role_id: int) -> Optional[Role]:
        model = self.db.query(RoleModel).filter(RoleModel.id == role_id).first()
        return _model_to_role(model) if model else None

    def find_by_name(self, name: str) -> Optional[Role]:
        model = self.db.query(RoleModel).filter(RoleModel.name == name).first()
        return _model_to_role(model) if model else None

    def find_all(self) -> list[Role]:
        return [_model_to_role(m) for m in self.db.query(RoleModel).all()]

    def save(self, role: Role) -> Role:
        model = RoleModel(name=role.name, description=role.description)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_role(model)