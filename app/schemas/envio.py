from pydantic import BaseModel, Field


class CotizacionRequest(BaseModel):
    direccion_destino: str = Field(min_length=5, max_length=255)


class CotizacionResponse(BaseModel):
    origen: str
    destino: str
    distancia_km: float
    costo_envio: float
