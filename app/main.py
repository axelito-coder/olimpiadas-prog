from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, envio, pedidos, productos
from app.core.config import get_settings
from app.db import session as db_session
from app.db.base import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=db_session.engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API REST desacoplada para el sistema Kiosco Don Pepe. "
        "Incluye autenticacion centralizada (JWT), gestion de productos y pedidos, "
        "e integracion con un servicio externo de mapas para cotizar envios."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(productos.router, prefix=settings.API_V1_PREFIX)
app.include_router(pedidos.router, prefix=settings.API_V1_PREFIX)
app.include_router(envio.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Salud"])
def health_check():
    return {"status": "ok"}
