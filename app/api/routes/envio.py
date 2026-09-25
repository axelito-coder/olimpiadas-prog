from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.envio import CotizacionRequest, CotizacionResponse
from app.services.geocoding import GeocodingError, cotizar_envio

router = APIRouter(prefix="/envio", tags=["Envio"])


@router.post("/cotizar", response_model=CotizacionResponse)
def cotizar(payload: CotizacionRequest, _current_user: Usuario = Depends(get_current_user)):
    try:
        return cotizar_envio(payload.direccion_destino)
    except GeocodingError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
