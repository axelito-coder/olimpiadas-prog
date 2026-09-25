"""Carga datos iniciales: un usuario administrador y productos de ejemplo.
Uso: python -m scripts.seed
"""

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.producto import Producto
from app.models.usuario import RolUsuario, Usuario


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Usuario).filter(Usuario.email == "admin@kiosco.com").first():
            admin = Usuario(
                nombre="Administrador",
                email="admin@kiosco.com",
                hashed_password=hash_password("admin123"),
                rol=RolUsuario.ADMIN,
            )
            db.add(admin)

        if db.query(Producto).count() == 0:
            productos = [
                Producto(nombre="Coca Cola 500ml", descripcion="Gaseosa", precio=1500, stock=50),
                Producto(nombre="Alfajor Jorgito", descripcion="Alfajor de chocolate", precio=900, stock=100),
                Producto(nombre="Papas Fritas Lays", descripcion="Snack salado", precio=2200, stock=30),
            ]
            db.add_all(productos)

        db.commit()
        print("Seed completado: admin@kiosco.com / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
