import httpx
import pytest
import respx

from app.services.geocoding import GeocodingError, cotizar_envio, geocode_address, haversine_km


@respx.mock
def test_geocode_address_devuelve_coordenadas():
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=httpx.Response(200, json=[{"lat": "-34.6534", "lon": "-58.6198"}])
    )
    lat, lon = geocode_address("Av. Rivadavia 1000, Moron, Buenos Aires, Argentina")
    assert lat == pytest.approx(-34.6534)
    assert lon == pytest.approx(-58.6198)


@respx.mock
def test_geocode_address_sin_resultados_lanza_error():
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=httpx.Response(200, json=[])
    )
    with pytest.raises(GeocodingError):
        geocode_address("direccion inexistente")


def test_haversine_distancia_cero_para_mismo_punto():
    assert haversine_km(-34.6, -58.4, -34.6, -58.4) == pytest.approx(0.0)


def test_haversine_distancia_conocida():
    # Moron -> Obelisco (aprox 15-20 km en linea recta)
    distancia = haversine_km(-34.6534, -58.6198, -34.6037, -58.3816)
    assert 15 < distancia < 25


@respx.mock
def test_cotizar_envio_calcula_costo_total():
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        side_effect=[
            httpx.Response(200, json=[{"lat": "-34.6534", "lon": "-58.6198"}]),
            httpx.Response(200, json=[{"lat": "-34.6037", "lon": "-58.3816"}]),
        ]
    )
    resultado = cotizar_envio("Av. 9 de Julio 1, CABA, Argentina")
    assert resultado["distancia_km"] > 0
    assert resultado["costo_envio"] > 0
