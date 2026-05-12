# Ruta: backend/app/contexts/products/application/use_cases.py

from app.contexts.products.domain.entities import Category, Product, Supplier
from app.contexts.products.domain.repositories import (
    CategoryRepository, ProductRepository, SupplierRepository,
)
from app.shared.exceptions import BusinessRuleViolation, EntityNotFound


class CreateProductUseCase:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def execute(self, **kwargs) -> Product:
        if self.product_repo.find_by_code(kwargs["code"]):
            raise BusinessRuleViolation(f"El código '{kwargs['code']}' ya está en uso.")
        product = Product(id=None, **kwargs)
        return self.product_repo.save(product)


class ListProductsUseCase:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def execute(self, active_only: bool = True) -> list[Product]:
        return self.product_repo.find_all(active_only=active_only)


class UpdateProductUseCase:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def execute(self, product_id: int, **kwargs) -> Product:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise EntityNotFound("Producto", product_id)
        for field, value in kwargs.items():
            if value is not None and hasattr(product, field):
                setattr(product, field, value)
        return self.product_repo.update(product)


class DeactivateProductUseCase:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def execute(self, product_id: int) -> None:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise EntityNotFound("Producto", product_id)
        self.product_repo.delete(product_id)


class CreateCategoryUseCase:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def execute(self, name: str, description: str = None) -> Category:
        category = Category(id=None, name=name, description=description)
        return self.category_repo.save(category)


class ListCategoriesUseCase:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def execute(self) -> list[Category]:
        return self.category_repo.find_all()


class CreateSupplierUseCase:
    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo

    def execute(self, **kwargs) -> Supplier:
        return self.supplier_repo.save(Supplier(id=None, **kwargs))


class ListSuppliersUseCase:
    def __init__(self, supplier_repo: SupplierRepository):
        self.supplier_repo = supplier_repo

    def execute(self) -> list[Supplier]:
        return self.supplier_repo.find_all()