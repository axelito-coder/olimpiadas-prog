def test_listar_productos_vacio(client):
    response = client.get("/api/v1/productos")
    assert response.status_code == 200
    assert response.json() == []


def test_crear_producto_requiere_admin(client, cliente_token):
    response = client.post(
        "/api/v1/productos",
        json={"nombre": "Coca Cola 500ml", "precio": 1500, "stock": 20},
        headers={"Authorization": f"Bearer {cliente_token}"},
    )
    assert response.status_code == 403


def test_crear_producto_como_admin(client, admin_token):
    response = client.post(
        "/api/v1/productos",
        json={"nombre": "Coca Cola 500ml", "descripcion": "Gaseosa", "precio": 1500, "stock": 20},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Coca Cola 500ml"
    assert body["stock"] == 20


def test_actualizar_y_eliminar_producto(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    crear = client.post(
        "/api/v1/productos",
        json={"nombre": "Alfajor", "precio": 800, "stock": 50},
        headers=headers,
    )
    producto_id = crear.json()["id"]

    actualizar = client.put(
        f"/api/v1/productos/{producto_id}", json={"stock": 45}, headers=headers
    )
    assert actualizar.status_code == 200
    assert actualizar.json()["stock"] == 45

    eliminar = client.delete(f"/api/v1/productos/{producto_id}", headers=headers)
    assert eliminar.status_code == 204

    obtener = client.get(f"/api/v1/productos/{producto_id}")
    assert obtener.status_code == 404


def test_producto_precio_invalido_rechazado(client, admin_token):
    response = client.post(
        "/api/v1/productos",
        json={"nombre": "Producto malo", "precio": -10, "stock": 1},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422
