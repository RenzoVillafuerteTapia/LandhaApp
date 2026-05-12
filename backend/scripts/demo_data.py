# Ruta: backend/scripts/demo_data.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app.contexts.iam.infrastructure.models
import app.contexts.products.infrastructure.models
import app.contexts.inventory.infrastructure.models
import app.contexts.transfers.infrastructure.models
import app.contexts.sales.infrastructure.models
import app.contexts.billing.infrastructure.models
import app.contexts.customers.infrastructure.models

from app.database import Base, SessionLocal, engine
from app.contexts.iam.infrastructure.models import RoleModel, UserModel
from app.contexts.products.infrastructure.models import CategoryModel, ProductModel
from app.contexts.inventory.infrastructure.models import (
    InventoryStockModel, InventoryMovementModel, StockLocationModel
)
from app.contexts.customers.infrastructure.models import CustomerModel
from app.shared.security import hash_password

Base.metadata.create_all(bind=engine)


def demo():
    db = SessionLocal()
    try:
        # ── Usuario vendedor ──────────────────────────────────────
        seller_role = db.query(RoleModel).filter(RoleModel.name == "seller").first()
        if seller_role:
            existing = db.query(UserModel).filter(UserModel.username == "vendedor1").first()
            if not existing:
                db.add(UserModel(
                    username="vendedor1",
                    email="vendedor1@landhaapp.com",
                    full_name="María García",
                    hashed_password=hash_password("vendedor123"),
                    role_id=seller_role.id,
                    is_active=True,
                ))
                print("✅ Usuario vendedor: vendedor1 / vendedor123")

        # ── Categorías ────────────────────────────────────────────
        cats = [
            ("Correderas y Rieles", "Sistemas de deslizamiento para cajones y puertas"),
            ("Bisagras", "Bisagras para muebles y puertas de todo tipo"),
            ("Jaladores y Tiradores", "Jaladores decorativos y funcionales"),
            ("Garruchas y Ruedas", "Ruedas y garruchas para muebles"),
            ("Sistemas de Cierre", "Cerraduras, pestillos y sistemas de seguridad"),
            ("Soportes y Esquineros", "Soportes metálicos y esquineros de refuerzo"),
            ("Accesorios Metálicos", "Herrajes varios y accesorios de ferretería fina"),
        ]
        cat_map = {}
        for name, desc in cats:
            existing = db.query(CategoryModel).filter(CategoryModel.name == name).first()
            if not existing:
                c = CategoryModel(name=name, description=desc)
                db.add(c)
                db.flush()
                cat_map[name] = c.id
            else:
                cat_map[name] = existing.id

        # ── Productos ─────────────────────────────────────────────
        products_data = [
            ("COR-001", "Corredera telescópica 45cm", "Corredera de extensión completa 45cm acero", "PAR", 12.50, "Correderas y Rieles"),
            ("COR-002", "Corredera telescópica 60cm", "Corredera de extensión completa 60cm acero", "PAR", 15.00, "Correderas y Rieles"),
            ("COR-003", "Corredera con amortiguador 45cm", "Sistema soft-close integrado", "PAR", 28.00, "Correderas y Rieles"),
            ("BIS-001", "Bisagra cazoleta 35mm clip", "Bisagra europea desmontable clip", "UND", 3.50, "Bisagras"),
            ("BIS-002", "Bisagra cazoleta soft-close", "Bisagra con cierre suave integrado", "UND", 6.80, "Bisagras"),
            ("BIS-003", "Bisagra de piano 1.80m", "Bisagra continua aluminio anodizado", "UND", 22.00, "Bisagras"),
            ("JAL-001", "Jalador barra acero 96mm", "Jalador tubular acero inox 96mm", "UND", 4.20, "Jaladores y Tiradores"),
            ("JAL-002", "Jalador barra acero 128mm", "Jalador tubular acero inox 128mm", "UND", 4.80, "Jaladores y Tiradores"),
            ("JAL-003", "Tirador gota bronce", "Tirador estilo clásico acabado bronce", "UND", 8.50, "Jaladores y Tiradores"),
            ("GAR-001", "Garrucha giratoria 50mm", "Rueda giratoria con freno 50mm", "UND", 5.50, "Garruchas y Ruedas"),
            ("GAR-002", "Garrucha giratoria 75mm", "Rueda giratoria capacidad 60kg", "UND", 8.00, "Garruchas y Ruedas"),
            ("CIE-001", "Cerradura mueble llave", "Cerradura embutida para muebles", "UND", 9.50, "Sistemas de Cierre"),
            ("CIE-002", "Cierre magnético", "Imán para puertas de mueble", "UND", 2.80, "Sistemas de Cierre"),
            ("CIE-003", "Pestillo corredera", "Pestillo deslizante acero inox", "UND", 4.50, "Sistemas de Cierre"),
            ("SOP-001", "Soporte estante 5mm", "Soporte pin para estantes 5mm", "UND", 0.80, "Soportes y Esquineros"),
            ("SOP-002", "Esquinero metálico 90°", "Escuadra refuerzo muebles 40x40mm", "UND", 2.50, "Soportes y Esquineros"),
            ("ACE-001", "Tornillo autorroscante 3.5x16", "Tornillo para madera punta fina caja x100", "CJA", 5.50, "Accesorios Metálicos"),
            ("ACE-002", "Clavija excéntrica confirmát", "Sistema de unión para tableros", "UND", 1.20, "Accesorios Metálicos"),
        ]

        prod_map = {}
        for code, name, desc, unit, price, cat_name in products_data:
            existing = db.query(ProductModel).filter(ProductModel.code == code).first()
            if not existing:
                p = ProductModel(
                    code=code, name=name, description=desc, unit=unit,
                    price=price, category_id=cat_map.get(cat_name), is_active=True
                )
                db.add(p)
                db.flush()
                prod_map[code] = p.id
            else:
                prod_map[code] = existing.id

        print(f"✅ {len(products_data)} productos cargados")

        # ── Stock inicial ─────────────────────────────────────────
        tienda = db.query(StockLocationModel).filter(StockLocationModel.name == "Tienda").first()
        almacen = db.query(StockLocationModel).filter(StockLocationModel.name == "Almacén").first()
        admin_user = db.query(UserModel).filter(UserModel.username == "admin").first()

        stock_tienda = {
            "COR-001": 20, "COR-002": 15, "COR-003": 8,
            "BIS-001": 100, "BIS-002": 60, "BIS-003": 5,
            "JAL-001": 50, "JAL-002": 50, "JAL-003": 20,
            "GAR-001": 30, "GAR-002": 20,
            "CIE-001": 15, "CIE-002": 40, "CIE-003": 25,
            "SOP-001": 200, "SOP-002": 80,
            "ACE-001": 30, "ACE-002": 150,
        }
        stock_almacen = {
            "COR-001": 50, "COR-002": 40, "COR-003": 20,
            "BIS-001": 300, "BIS-002": 150, "BIS-003": 12,
            "JAL-001": 120, "JAL-002": 120, "JAL-003": 45,
            "GAR-001": 80, "GAR-002": 50,
            "CIE-001": 35, "CIE-002": 100, "CIE-003": 60,
            "SOP-001": 500, "SOP-002": 200,
            "ACE-001": 80, "ACE-002": 400,
        }

        def set_stock(location, stock_dict):
            for code, qty in stock_dict.items():
                prod_id = prod_map.get(code)
                if not prod_id:
                    continue
                existing = db.query(InventoryStockModel).filter(
                    InventoryStockModel.product_id == prod_id,
                    InventoryStockModel.location_id == location.id,
                ).first()
                if not existing:
                    db.add(InventoryStockModel(
                        product_id=prod_id, location_id=location.id, quantity=qty
                    ))
                    db.add(InventoryMovementModel(
                        product_id=prod_id, location_id=location.id,
                        user_id=admin_user.id, movement_type="in",
                        quantity=qty, reference="stock_inicial",
                        notes="Carga inicial de inventario",
                    ))

        if tienda:
            set_stock(tienda, stock_tienda)
            print("✅ Stock cargado en Tienda")
        if almacen:
            set_stock(almacen, stock_almacen)
            print("✅ Stock cargado en Almacén")

        # ── Clientes de prueba ────────────────────────────────────
        customers = [
            dict(name="Cliente General", document_type="DNI", document_number="00000000"),
            dict(name="Juan Pérez Torres", document_type="DNI", document_number="45678901",
                 email="juan.perez@gmail.com", phone="987654321"),
            dict(name="Ana Rodríguez Silva", document_type="DNI", document_number="32145678",
                 phone="956789012"),
            dict(name="Mueblería El Roble SAC", document_type="RUC", document_number="20512345678",
                 business_name="Mueblería El Roble SAC", email="compras@elroble.pe", phone="014567890"),
            dict(name="Carpintería Moderna EIRL", document_type="RUC", document_number="20498765432",
                 business_name="Carpintería Moderna EIRL", phone="012345678"),
            dict(name="Carlos Mendoza", document_type="DNI", document_number="71234567",
                 phone="999888777"),
        ]

        added = 0
        for c in customers:
            existing = db.query(CustomerModel).filter(
                CustomerModel.document_number == c.get("document_number")
            ).first()
            if not existing:
                db.add(CustomerModel(**c))
                added += 1

        print(f"✅ {added} clientes de prueba cargados")
        db.commit()

        print("\n─────────────────────────────────────────")
        print("🎉 Datos de demo cargados exitosamente")
        print("─────────────────────────────────────────")
        print("👤 Vendedor:  vendedor1 / vendedor123")
        print("👤 Admin:     admin / admin123")
        print("─────────────────────────────────────────")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    demo()