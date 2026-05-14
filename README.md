# SistemaTiendaBACK

REST API backend para un sistema de control de caja, construido con FastAPI y PostgreSQL. Gestiona el inventario de efectivo (billetes y monedas) y el historial de transacciones.

## Stack

| Capa | Tecnología |
|------|------------|
| Framework | FastAPI |
| Base de datos | PostgreSQL |
| Driver DB | psycopg2 |
| Servidor ASGI | Uvicorn |
| Lenguaje | Python 3.10+ |

## Requisitos previos

- Python 3.10 o superior
- PostgreSQL 13 o superior

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/G-Gamboa/SistemaTiendaBACK.git
cd SistemaTiendaBACK
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/tienda_db
ALLOWED_ORIGINS=http://localhost:3000
```

### 5. Inicializar la base de datos

```bash
psql -U <usuario> -d <base_de_datos> -f schema.sql
```

### 6. Ejecutar el servidor

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.

## Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/tienda_db` |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos, separados por coma | `http://localhost:3000,https://miapp.com` |

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado de la API |
| `GET` | `/api/inventory` | Inventario actual de efectivo |
| `POST` | `/api/transaction` | Registrar una transacción |
| `GET` | `/api/transactions` | Historial de los últimos 30 días |

### GET /api/inventory

Devuelve la cantidad de cada denominación en caja.

```json
{
  "100": 5,
  "50": 3,
  "20": 10
}
```

### POST /api/transaction

Registra una transacción y actualiza el inventario de efectivo.

**Body:**

```json
{
  "transaction_type": "venta",
  "sale_amount": 50.00,
  "received_amount": 100.00,
  "change_amount": 50.00,
  "money_in": { "100": 1 },
  "money_out": { "50": 1 },
  "notes": ""
}
```

**Respuesta:**

```json
{
  "status": "success",
  "message": "Transacción registrada exitosamente"
}
```

### GET /api/transactions

Devuelve las transacciones de los últimos 30 días ordenadas de más reciente a más antigua.

## Documentación interactiva

FastAPI genera documentación automática disponible con el servidor en ejecución:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
