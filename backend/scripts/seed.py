# Ruta: backend/scripts/seed.py

"""
Ejecutar con:
    cd backend
    python -m scripts.seed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, SessionLocal, engine
from app.contexts.iam.infrastructure.models import RoleModel, UserModel
from app.contexts.inventory.infrastructure.models import StockLocationModel
from app.shared.security import hash_password

import app.contexts.iam.infrastructure.models  # noqa
import app.contexts.products.infrastructure.models  # noqa
import app.contexts.inventory.infrastructure.models  # noqa
import app.contexts.transfers.infrastructure.models  # noqa
import app.contexts.sales.infrastructure.models  # noqa
import app.contexts.billing.infrastructure.models  # noqa
import app.contexts.customers.infrastructure.models  # noqa


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Roles
        admin_role = db.query(RoleModel).filter(RoleModel.name == "admin").first()
        if not admin_role:
            admin_role = RoleModel(name="admin", description="Administrador del sistema")
            db.add(admin_role)

        seller_role = db.query(RoleModel).filter(RoleModel.name == "seller").first()
        if not seller_role:
            seller_role = RoleModel(name="seller", description="Vendedor")
            db.add(seller_role)

        db.flush()

        # Usuario administrador
        admin_user = db.query(UserModel).filter(UserModel.username == "admin").first()
        if not admin_user:
            admin_user = UserModel(
                username="admin",
                email="admin@landhaapp.com",
                full_name="Administrador LandhaApp",
                hashed_password=hash_password("admin123"),
                role_id=admin_role.id,
                is_active=True,
            )
            db.add(admin_user)

        # Ubicaciones
        store = db.query(StockLocationModel).filter(StockLocationModel.name == "Tienda").first()
        if not store:
            db.add(StockLocationModel(name="Tienda", type="store"))

        warehouse = db.query(StockLocationModel).filter(StockLocationModel.name == "Almacén").first()
        if not warehouse:
            db.add(StockLocationModel(name="Almacén", type="warehouse"))

        db.commit()
        print("✅  Seed completado:")
        print("    Roles: admin, seller")
        print("    Usuario: admin / admin123")
        print("    Ubicaciones: Tienda, Almacén")

    except Exception as e:
        db.rollback()
        print(f"❌  Error en seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()