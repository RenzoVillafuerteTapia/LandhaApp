# Ruta: backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.shared.exceptions import register_exception_handlers

# Importar todos los modelos ORM para que SQLAlchemy los registre
import app.contexts.iam.infrastructure.models  # noqa: F401
import app.contexts.products.infrastructure.models  # noqa: F401
import app.contexts.inventory.infrastructure.models  # noqa: F401
import app.contexts.transfers.infrastructure.models  # noqa: F401
import app.contexts.sales.infrastructure.models  # noqa: F401
import app.contexts.billing.infrastructure.models  # noqa: F401
import app.contexts.customers.infrastructure.models  # noqa: F401

# Importar routers
from app.contexts.iam.interfaces.router import router as iam_router
from app.contexts.products.interfaces.router import router as products_router
from app.contexts.inventory.interfaces.router import router as inventory_router
from app.contexts.transfers.interfaces.router import router as transfers_router
from app.contexts.sales.interfaces.router import router as sales_router
from app.contexts.billing.interfaces.router import router as billing_router
from app.contexts.customers.interfaces.router import router as customers_router

# Crear tablas (en producción usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API para gestión de ventas, inventario y comprobantes — LandhaApp",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejadores de error centralizados
register_exception_handlers(app)

# Routers
app.include_router(iam_router, prefix="/auth", tags=["Auth"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])
app.include_router(sales_router, prefix="/sales", tags=["Sales"])
app.include_router(billing_router, prefix="/billing", tags=["Billing"])
app.include_router(customers_router, prefix="/customers", tags=["Customers"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.app_name}