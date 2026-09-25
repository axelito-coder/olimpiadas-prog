import httpx
import respx


@respx.mock
def test_cotizar_envio_ok(client, cliente_token):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        side_effect=[
            httpx.Response(200, json=[{"lat": "-34.6534", "lon": "-58.6198"}]),
            httpx.Response(200, json=[{"lat": "-34.6037", "lon": "-58.3816"}]),
        ]
    )
    response = client.post(
        "/api/v1/envio/cotizar",
        json={"direccion_destino": "Av. 9 de Julio 1, CABA, Argentina"},
        headers={"Authorization": f"Bearer {cliente_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["distancia_km"] > 0
    assert body["costo_envio"] > 0


def test_cotizar_envio_requiere_autenticacion(client):
    response = client.post(
        "/api/v1/envio/cotizar", json={"direccion_destino": "Av. 9 de Julio 1, CABA, Argentina"}
    )
    assert response.status_code == 401


@respx.mock
def test_cotizar_envio_direccion_no_encontrada(client, cliente_token):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=httpx.Response(200, json=[])
    )
    response = client.post(
        "/api/v1/envio/cotizar",
        json={"direccion_destino": "direccion que no existe en ningun lado 12345"},
        headers={"Authorization": f"Bearer {cliente_token}"},
    )
    assert response.status_code == 502
