# Ruta: backend/app/shared/exceptions.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainException(Exception):
    """Base para todas las excepciones de dominio."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EntityNotFound(DomainException):
    def __init__(self, entity: str, entity_id):
        super().__init__(f"{entity} con id '{entity_id}' no encontrado.", 404)


class InsufficientStock(DomainException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            f"Stock insuficiente para '{product_name}'. "
            f"Disponible: {available}, solicitado: {requested}.",
            422,
        )


class BusinessRuleViolation(DomainException):
    def __init__(self, message: str):
        super().__init__(message, 422)


class AuthenticationError(DomainException):
    def __init__(self, message: str = "Credenciales inválidas."):
        super().__init__(message, 401)


class AuthorizationError(DomainException):
    def __init__(self, message: str = "No tiene permisos para realizar esta acción."):
        super().__init__(message, 403)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Error interno del servidor."},
        )