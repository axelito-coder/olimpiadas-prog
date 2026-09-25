from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.pedido import EstadoPedido


class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class DetallePedidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float


class PedidoCreate(BaseModel):
    direccion_envio: str = Field(min_length=5, max_length=255)
    items: list[DetallePedidoCreate] = Field(min_length=1)


class PedidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    fecha: datetime
    estado: EstadoPedido
    direccion_envio: str | None
    costo_envio: float
    total: float
    detalles: list[DetallePedidoOut]


class PedidoEstadoUpdate(BaseModel):
    estado: EstadoPedido
