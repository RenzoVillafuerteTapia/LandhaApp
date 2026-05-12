# Ruta: backend/app/contexts/products/infrastructure/repositories.py

from typing import Optional
from sqlalchemy.orm import Session

from app.contexts.products.domain.entities import Category, Product, Supplier
from app.contexts.products.domain.repositories import (
    CategoryRepository, ProductRepository, SupplierRepository,
)
from app.contexts.products.infrastructure.models import (
    CategoryModel, ProductModel, SupplierModel,
)


def _to_product(m: ProductModel) -> Product:
    return Product(
        id=m.id, code=m.code, name=m.name, description=m.description,
        unit=m.unit, price=float(m.price),
        category_id=m.category_id,
        supplier_id=m.supplier_id,
        category_name=m.category.name if m.category else None,
        supplier_name=m.supplier.name if m.supplier else None,
        is_active=m.is_active,
    )


def _to_category(m: CategoryModel) -> Category:
    return Category(id=m.id, name=m.name, description=m.description)


def _to_supplier(m: SupplierModel) -> Supplier:
    return Supplier(id=m.id, name=m.name, ruc=m.ruc, phone=m.phone,
                    email=m.email, address=m.address)


class SqlProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, product_id: int) -> Optional[Product]:
        m = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return _to_product(m) if m else None

    def find_by_code(self, code: str) -> Optional[Product]:
        m = self.db.query(ProductModel).filter(ProductModel.code == code).first()
        return _to_product(m) if m else None

    def find_all(self, active_only: bool = True) -> list[Product]:
        q = self.db.query(ProductModel)
        if active_only:
            q = q.filter(ProductModel.is_active == True)
        return [_to_product(m) for m in q.all()]

    def save(self, product: Product) -> Product:
        m = ProductModel(
            code=product.code, name=product.name, description=product.description,
            unit=product.unit, price=product.price,
            category_id=product.category_id, supplier_id=product.supplier_id,
            is_active=product.is_active,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return _to_product(m)

    def update(self, product: Product) -> Product:
        m = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
        m.code = product.code
        m.name = product.name
        m.description = product.description
        m.unit = product.unit
        m.price = product.price
        m.category_id = product.category_id
        m.supplier_id = product.supplier_id
        m.is_active = product.is_active
        self.db.commit()
        self.db.refresh(m)
        return _to_product(m)

    def delete(self, product_id: int) -> None:
        m = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if m:
            m.is_active = False
            self.db.commit()


class SqlCategoryRepository(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, cid: int) -> Optional[Category]:
        m = self.db.query(CategoryModel).filter(CategoryModel.id == cid).first()
        return _to_category(m) if m else None

    def find_all(self) -> list[Category]:
        return [_to_category(m) for m in self.db.query(CategoryModel).all()]

    def save(self, category: Category) -> Category:
        m = CategoryModel(name=category.name, description=category.description)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return _to_category(m)

    def update(self, category: Category) -> Category:
        m = self.db.query(CategoryModel).filter(CategoryModel.id == category.id).first()
        m.name = category.name
        m.description = category.description
        self.db.commit()
        self.db.refresh(m)
        return _to_category(m)


class SqlSupplierRepository(SupplierRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, sid: int) -> Optional[Supplier]:
        m = self.db.query(SupplierModel).filter(SupplierModel.id == sid).first()
        return _to_supplier(m) if m else None

    def find_all(self) -> list[Supplier]:
        return [_to_supplier(m) for m in self.db.query(SupplierModel).all()]

    def save(self, supplier: Supplier) -> Supplier:
        m = SupplierModel(name=supplier.name, ruc=supplier.ruc, phone=supplier.phone,
                          email=supplier.email, address=supplier.address)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return _to_supplier(m)