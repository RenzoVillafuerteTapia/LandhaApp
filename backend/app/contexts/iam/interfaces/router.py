# Ruta: backend/app/contexts/iam/interfaces/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contexts.iam.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    ListUsersUseCase,
    LoginUseCase,
    UpdateUserUseCase,
)
from app.contexts.iam.infrastructure.repositories import (
    SqlRoleRepository,
    SqlUserRepository,
)
from app.contexts.iam.interfaces.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.database import get_db
from app.shared.dependencies import get_current_user, require_admin

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    repo = SqlUserRepository(db)
    use_case = LoginUseCase(repo)
    return use_case.execute(payload.username, payload.password)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    repo = SqlUserRepository(db)
    return ListUsersUseCase(repo).execute()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    user_repo = SqlUserRepository(db)
    role_repo = SqlRoleRepository(db)
    use_case = CreateUserUseCase(user_repo, role_repo)
    return use_case.execute(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role_id=payload.role_id,
    )


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    user_repo = SqlUserRepository(db)
    role_repo = SqlRoleRepository(db)
    use_case = UpdateUserUseCase(user_repo, role_repo)
    return use_case.execute(user_id, **payload.model_dump(exclude_none=True))


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    repo = SqlUserRepository(db)
    DeleteUserUseCase(repo).execute(user_id)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = SqlUserRepository(db)
    user = repo.find_by_id(int(current_user["sub"]))
    return user