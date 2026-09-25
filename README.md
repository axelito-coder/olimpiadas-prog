# Kiosco Don Pepe API

API REST desacoplada para la modernizacion del sistema **Kiosco Don Pepe**, desarrollada como
resolucion del caso de estudio de las Olimpiadas Institucionales de Programacion (E.E.S.T. N°6
"Chacabuco" — 7° año). Reemplaza el monolito original en ASP.NET MVC por una arquitectura de
servicios con autenticacion centralizada, integracion externa, testing automatizado, pipeline
CI/CD y despliegue en contenedores.

## 1. Arquitectura del sistema

```mermaid
flowchart LR
    subgraph Cliente
        WEB["Cliente Web / App / Postman"]
    end

    subgraph API["Kiosco Don Pepe API (FastAPI)"]
        GW["API Gateway / Router"]
        AUTH["Modulo Auth\n(JWT / OAuth2)"]
        PROD["Modulo Productos"]
        PED["Modulo Pedidos"]
        ENV["Modulo Envio"]
    end

    DB[(PostgreSQL)]
    MAPS["Servicio externo\nNominatim (OpenStreetMap)\nGeocoding"]

    WEB -->|HTTPS + JWT| GW
    GW --> AUTH
    GW --> PROD
    GW --> PED
    GW --> ENV
    AUTH --> DB
    PROD --> DB
    PED --> DB
    ENV -->|HTTP| MAPS
    PED --> ENV
```

- **API Gateway / Router**: unico punto de entrada (`app/main.py`), monta los modulos y aplica CORS.
- **Auth**: registro/login con JWT (OAuth2 Password Flow), passwords hasheados con bcrypt.
- **Productos**: catalogo del kiosco (CRUD, escritura restringida a rol `admin`).
- **Pedidos**: carrito/ticket de compra, descuenta stock y calcula costo de envio.
- **Envio**: integra el servicio externo de mapas (Nominatim/OpenStreetMap) para geocodificar
  direcciones y calcular distancia (formula de Haversine) y costo de envio.
- **PostgreSQL**: persistencia relacional via SQLAlchemy ORM.

## 2. Modelo de datos

- `Usuario` (id, nombre, email, hashed_password, rol: cliente/admin)
- `Producto` (id, nombre, descripcion, precio, stock)
- `Pedido` (id, usuario_id, fecha, estado, direccion_envio, costo_envio, total)
- `DetallePedido` (id, pedido_id, producto_id, cantidad, precio_unitario)

## 3. Endpoints principales

| Metodo | Endpoint | Auth | Descripcion |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Publico | Crea un usuario (rol cliente) |
| POST | `/api/v1/auth/login` | Publico | Devuelve un JWT (`access_token`) |
| GET | `/api/v1/auth/me` | JWT | Datos del usuario autenticado |
| GET | `/api/v1/productos` | Publico | Lista el catalogo |
| GET | `/api/v1/productos/{id}` | Publico | Detalle de un producto |
| POST | `/api/v1/productos` | JWT admin | Crea un producto |
| PUT | `/api/v1/productos/{id}` | JWT admin | Actualiza un producto |
| DELETE | `/api/v1/productos/{id}` | JWT admin | Elimina un producto |
| POST | `/api/v1/pedidos` | JWT | Crea un pedido (descuenta stock, cotiza envio) |
| GET | `/api/v1/pedidos/me` | JWT | Pedidos del usuario autenticado |
| GET | `/api/v1/pedidos` | JWT admin | Lista todos los pedidos |
| GET | `/api/v1/pedidos/{id}` | JWT (dueño o admin) | Detalle de un pedido |
| PATCH | `/api/v1/pedidos/{id}/estado` | JWT admin | Cambia el estado del pedido |
| POST | `/api/v1/envio/cotizar` | JWT | Cotiza distancia/costo de envio a una direccion |
| GET | `/health` | Publico | Health check |

Documentacion interactiva autogenerada (Swagger UI): `http://localhost:8000/docs`.

## 4. Testing automatizado

- **Unitarios**: `tests/test_security.py` (JWT, hashing), `tests/test_geocoding.py`
  (geocoding y calculo de distancia, con el servicio externo mockeado via `respx`).
- **Integracion**: `tests/test_auth_api.py`, `tests/test_productos_api.py`,
  `tests/test_pedidos_api.py`, `tests/test_envio_api.py` — usan `TestClient` de FastAPI contra
  una base SQLite en memoria.

Ejecutar localmente:

```bash
pip install -r requirements-dev.txt
pytest
```

Esto genera un reporte de cobertura en consola y un `coverage.xml`.

## 5. Pipeline de CI/CD

Definido en [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml):

1. **Lint** con `ruff`.
2. **Tests** con `pytest` (+ reporte de cobertura como artifact).
3. **Build y push de la imagen Docker** a GitHub Container Registry (`ghcr.io`) cuando se hace
   push a `main` (solo si el job de tests fue exitoso).

## 6. Despliegue con Docker

### Requisitos
- Docker y Docker Compose instalados.

### Pasos

```bash
cp .env.example .env
# editar .env si hace falta (JWT_SECRET_KEY, direccion del kiosco, etc.)

docker compose up --build
```

Esto levanta:
- `db`: PostgreSQL 16 en el puerto `5432`.
- `api`: la API FastAPI en `http://localhost:8000` (crea las tablas automaticamente al arrancar).

Cargar datos de ejemplo (usuario admin + productos):

```bash
docker compose exec api python -m scripts.seed
```

Credenciales de ejemplo: `admin@kiosco.com` / `admin123`.

### Despliegue sin Docker Compose (manual)

```bash
python -m venv .venv
source .venv/bin/activate  # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://usuario:clave@host:5432/kiosco_don_pepe
export JWT_SECRET_KEY=una-clave-segura
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 7. Origen del proyecto

Este proyecto retoma el dominio del sistema **Kiosco Don Pepe** (ASP.NET MVC monolitico,
`https://github.com/rodriyjaz1988-hue/Kiosco_Don_Pepe`) y lo reconstruye como una API REST
desacoplada para cumplir con los requisitos de arquitectura avanzada, integracion de sistemas,
testing automatizado y DevOps del caso de estudio.
