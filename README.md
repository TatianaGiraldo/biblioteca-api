# Biblioteca API

API REST para la gestión de libros y préstamos de una biblioteca, construida con **FastAPI**, **SQLAlchemy** y **SQLite**.

## Stack

- **Python 3.10+**
- **FastAPI** — framework web
- **SQLAlchemy** — ORM
- **SQLite** — base de datos (archivo `biblioteca.db`)
- **Alembic** — migraciones
- **Pytest + httpx** — pruebas
- **Uvicorn** — servidor ASGI

## Estructura del proyecto

```
biblioteca-api/
├── app/
│   ├── __init__.py
│   ├── main.py                # Punto de entrada (FastAPI app + lifespan)
│   ├── database.py            # Conexión SQLAlchemy / sesión / Base
│   ├── models/                # Modelos ORM
│   │   ├── libro.py
│   │   └── prestamo.py
│   ├── schemas/               # Schemas Pydantic
│   │   ├── libro.py
│   │   └── prestamo.py
│   ├── routers/               # Endpoints HTTP
│   │   ├── libros.py
│   │   └── prestamos.py
│   ├── services/              # Lógica de negocio
│   │   └── prestamo_service.py
│   └── seed.py                # Carga 20 libros al iniciar la app
├── tests/
│   └── test_prestamos.py      # Pruebas de todos los endpoints
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalación

### 1. Clonar el repositorio

```bash
git clone git@github.com:TatianaGiraldo/biblioteca-api.git
cd biblioteca-api
```

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecución

### Levantar el servidor

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en:

- **API**: http://localhost:8000
- **Documentación interactiva (Swagger UI)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

Al iniciar por primera vez:
- Se crea el archivo `biblioteca.db` con las tablas `libros` y `prestamos`
- Se siembran automáticamente 20 libros de ejemplo (solo si la tabla está vacía)

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/libros/{isbn}/disponibilidad`     | Consulta disponibilidad de un libro |
| `POST` | `/prestamos`                        | Registra un nuevo préstamo |
| `PUT`  | `/prestamos/{id}/devolucion`        | Registra la devolución de un préstamo |
| `GET`  | `/prestamos/vencidos`               | Lista los préstamos vencidos y activos |

### Reglas de negocio

- Al registrar un préstamo, `fecha_vencimiento = fecha_prestamo + 15 días`
- Si no se envía `fecha_prestamo`, se usa la fecha de hoy
- El préstamo se crea con estado `ACTIVO`
- Al registrar la devolución, el estado pasa a `DEVUELTO` y se restituye un ejemplar
- No se permiten préstamos si `ejemplares_disponibles == 0` (HTTP 400)
- No se permite devolver un préstamo que ya fue devuelto (HTTP 400)

### Ejemplos

**Registrar un préstamo:**

```bash
curl -X POST http://localhost:8000/prestamos \
  -H "Content-Type: application/json" \
  -d '{
    "isbn_libro": "978-0132350884",
    "identificacion_usuario": "CC1234567",
    "fecha_prestamo": "2026-05-22"
  }'
```

**Registrar una devolución:**

```bash
curl -X PUT http://localhost:8000/prestamos/<UUID>/devolucion
```

**Consultar disponibilidad:**

```bash
curl http://localhost:8000/libros/978-0132350884/disponibilidad
```

**Listar préstamos vencidos:**

```bash
curl http://localhost:8000/prestamos/vencidos
```

## Pruebas

Las pruebas usan una base de datos SQLite en memoria, por lo que no afectan a `biblioteca.db`.

```bash
pytest tests/ -v
```

## Migraciones (Alembic)

Inicializar Alembic (solo la primera vez):

```bash
alembic init alembic
```

Generar una nueva migración:

```bash
alembic revision --autogenerate -m "descripcion del cambio"
```

Aplicar migraciones:

```bash
alembic upgrade head
```

## Notas

- La base de datos `biblioteca.db` se ignora en `.gitignore` (no se versiona)
- Los modelos se crean automáticamente al arrancar la app vía `Base.metadata.create_all`
- Para producción se recomienda usar Alembic en lugar de `create_all`
