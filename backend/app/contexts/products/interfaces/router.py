# Ruta: backend/app/contexts/products/interfaces/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contexts.products.application.use_cases import (
    CreateCategoryUseCase, CreateProductUseCase, CreateSupplierUseCase,
    DeactivateProductUseCase, ListCategoriesUseCase, ListProductsUseCase,
    ListSuppliersUseCase, UpdateProductUseCase,
)
from app.contexts.products.infrastructure.repositories import (
    SqlCategoryRepository, SqlProductRepository, SqlSupplierRepository,
)
from app.contexts.products.interfaces.schemas import (
    CategoryCreate, CategoryResponse,
    ProductCreate, ProductResponse, ProductUpdate,
    SupplierCreate, SupplierResponse,
)
from app.database import get_db
from app.shared.dependencies import get_current_user, require_admin

router = APIRouter()


# ─── Categories ──────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ListCategoriesUseCase(SqlCategoryRepository(db)).execute()


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return CreateCategoryUseCase(SqlCategoryRepository(db)).execute(
        name=payload.name, description=payload.description
    )


# ─── Suppliers ───────────────────────────────────────────────────────────────

@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ListSuppliersUseCase(SqlSupplierRepository(db)).execute()


@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return CreateSupplierUseCase(SqlSupplierRepository(db)).execute(**payload.model_dump())


# ─── Products ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ProductResponse])
def list_products(
    active_only: bool = True,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return ListProductsUseCase(SqlProductRepository(db)).execute(active_only=active_only)


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return CreateProductUseCase(SqlProductRepository(db)).execute(**payload.model_dump())


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return UpdateProductUseCase(SqlProductRepository(db)).execute(
        product_id, **payload.model_dump(exclude_none=True)
    )


@router.delete("/{product_id}", status_code=204)
def deactivate_product(product_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    DeactivateProductUseCase(SqlProductRepository(db)).execute(product_id)