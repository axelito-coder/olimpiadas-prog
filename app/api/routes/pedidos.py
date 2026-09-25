from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.pedido import DetallePedido, Pedido
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.pedido import PedidoCreate, PedidoEstadoUpdate, PedidoOut
from app.services.geocoding import GeocodingError, cotizar_envio

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    payload: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    detalles: list[DetallePedido] = []
    total = 0.0

    for item in payload.items:
        producto = db.get(Producto, item.producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {item.producto_id} no encontrado",
            )
        if producto.stock < item.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para '{producto.nombre}'",
            )
        producto.stock -= item.cantidad
        subtotal = float(producto.precio) * item.cantidad
        total += subtotal
        detalles.append(
            DetallePedido(
                producto_id=producto.id,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
            )
        )

    try:
        cotizacion = cotizar_envio(payload.direccion_envio)
        costo_envio = cotizacion["costo_envio"]
    except GeocodingError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    pedido = Pedido(
        usuario_id=current_user.id,
        direccion_envio=payload.direccion_envio,
        costo_envio=costo_envio,
        total=total + costo_envio,
        detalles=detalles,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


@router.get("/me", response_model=list[PedidoOut])
def mis_pedidos(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(Pedido).filter(Pedido.usuario_id == current_user.id).all()


@router.get("", response_model=list[PedidoOut])
def listar_pedidos(db: Session = Depends(get_db), _admin: Usuario = Depends(get_current_admin)):
    return db.query(Pedido).all()


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(
    pedido_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if pedido.usuario_id != current_user.id and current_user.rol.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return pedido


@router.patch("/{pedido_id}/estado", response_model=PedidoOut)
def actualizar_estado(
    pedido_id: int,
    payload: PedidoEstadoUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    pedido.estado = payload.estado
    db.commit()
    db.refresh(pedido)
    return pedido
