import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import session as db_session
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# El lifespan de la app crea las tablas usando app.db.session.engine: lo apuntamos
# a la base de test en memoria para que TestClient() no intente conectarse a Postgres.
db_session.engine = engine


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"nombre": "Admin", "email": "admin@kiosco.com", "password": "admin123"},
    )
    # promover a admin directamente en la base de datos de test
    db = TestingSessionLocal()
    from app.models.usuario import RolUsuario, Usuario

    user = db.query(Usuario).filter(Usuario.email == "admin@kiosco.com").first()
    user.rol = RolUsuario.ADMIN
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@kiosco.com", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def cliente_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"nombre": "Cliente Uno", "email": "cliente@kiosco.com", "password": "cliente123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "cliente@kiosco.com", "password": "cliente123"},
    )
    return response.json()["access_token"]
