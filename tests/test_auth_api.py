def test_registro_y_login_exitoso(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"nombre": "Juan Perez", "email": "juan@kiosco.com", "password": "secreto123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "juan@kiosco.com"
    assert body["rol"] == "cliente"

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "juan@kiosco.com", "password": "secreto123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_registro_duplicado_falla(client):
    payload = {"nombre": "Juan", "email": "dup@kiosco.com", "password": "secreto123"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_login_credenciales_invalidas(client):
    response = client.post(
        "/api/v1/auth/login", data={"username": "noexiste@kiosco.com", "password": "x"}
    )
    assert response.status_code == 401


def test_me_requiere_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_con_token_valido(client, cliente_token):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {cliente_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "cliente@kiosco.com"
