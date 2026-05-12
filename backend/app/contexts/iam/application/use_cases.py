# Ruta: backend/app/contexts/iam/application/use_cases.py

from app.contexts.iam.domain.entities import User
from app.contexts.iam.domain.repositories import RoleRepository, UserRepository
from app.shared.exceptions import (
    AuthenticationError,
    BusinessRuleViolation,
    EntityNotFound,
)
from app.shared.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class LoginUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, username: str, password: str) -> dict:
        user = self.user_repo.find_by_username(username)
        if not user:
            raise AuthenticationError()
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError()
        if not user.is_active:
            raise AuthenticationError("Usuario inactivo.")

        token = create_access_token({
            "sub": str(user.id),
            "username": user.username,
            "role": user.role_name,
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": user.role_name,
        }


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def execute(self, username: str, email: str, full_name: str, password: str, role_id: int) -> User:
        if self.user_repo.find_by_username(username):
            raise BusinessRuleViolation(f"El usuario '{username}' ya existe.")
        if self.user_repo.find_by_email(email):
            raise BusinessRuleViolation(f"El email '{email}' ya está registrado.")

        role = self.role_repo.find_by_id(role_id)
        if not role:
            raise EntityNotFound("Rol", role_id)

        user = User(
            id=None,
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role_id=role_id,
            role_name=role.name,
        )
        return self.user_repo.save(user)


class ListUsersUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self) -> list[User]:
        return self.user_repo.find_all()


class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def execute(self, user_id: int, **kwargs) -> User:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFound("Usuario", user_id)

        if "password" in kwargs and kwargs["password"]:
            kwargs["hashed_password"] = hash_password(kwargs.pop("password"))
        else:
            kwargs.pop("password", None)

        if "role_id" in kwargs and kwargs["role_id"]:
            role = self.role_repo.find_by_id(kwargs["role_id"])
            if not role:
                raise EntityNotFound("Rol", kwargs["role_id"])

        for field, value in kwargs.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)

        return self.user_repo.update(user)


class DeleteUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: int) -> None:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise EntityNotFound("Usuario", user_id)
        self.user_repo.delete(user_id)