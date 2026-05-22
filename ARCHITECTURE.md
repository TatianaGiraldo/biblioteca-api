# Arquitectura — Biblioteca API

Este documento describe las decisiones técnicas y arquitectónicas del proyecto, las herramientas utilizadas durante su construcción y las mejoras pendientes.

---

## 1. Arquitectura elegida: arquitectura por capas

Se eligió una **arquitectura por capas** con tres niveles bien definidos:

```
┌────────────────────────────────────────────────┐
│  Router (app/routers/)                         │
│  Recibe peticiones HTTP, valida con Pydantic,  │
│  delega al servicio y devuelve la respuesta.   │
└───────────────────┬────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│  Service (app/services/)                       │
│  Contiene la lógica de negocio y las reglas    │
│  (validaciones de dominio, cálculo de fechas,  │
│  actualización de ejemplares, etc.).           │
└───────────────────┬────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────┐
│  Model (app/models/)                           │
│  Define las entidades persistentes y sus       │
│  relaciones mediante SQLAlchemy ORM.           │
└────────────────────────────────────────────────┘
```

**Apoyado por dos capas auxiliares:**
- `app/schemas/` — Schemas Pydantic para entrada/salida HTTP (DTOs).
- `app/database.py` — Configuración del engine, `SessionLocal` y dependencia `get_db()`.

### ¿Por qué esta arquitectura?

| Razón | Beneficio |
|------|-----------|
| **Separación de responsabilidades** | Cada capa tiene una sola razón para cambiar (SRP). El router cambia si cambian las rutas; el service cambia si cambian las reglas de negocio; el model cambia si cambia el esquema de datos. |
| **Testabilidad** | Los services son funciones puras (reciben `db` por parámetro) y se pueden testear sin levantar el servidor. Los routers se prueban con `TestClient` y `dependency_overrides`. |
| **Reutilización** | La lógica de negocio del service puede invocarse desde otros contextos (CLI, scripts, otro endpoint) sin duplicar código. |
| **Escalabilidad del equipo** | Permite que distintas personas trabajen en distintas capas sin colisiones. |
| **Cambio de framework/DB con menor impacto** | Si mañana cambiamos FastAPI por otro framework o SQLite por PostgreSQL, las capas inferiores siguen iguales. |

### Flujo de una petición típica (`POST /prestamos`)

1. **Router** — `app/routers/prestamos.py` recibe el JSON, lo valida contra `PrestamoCreate` (Pydantic).
2. **Service** — `app/services/prestamo_service.py` ejecuta las reglas:
   - Valida que el libro exista (lanza `HTTPException 404` si no).
   - Valida que haya ejemplares disponibles (lanza `HTTPException 400` si no).
   - Calcula `fecha_vencimiento = fecha_prestamo + 15 días`.
   - Decrementa `ejemplares_disponibles` del libro.
   - Crea el `Prestamo` con estado `ACTIVO`.
3. **Model** — SQLAlchemy persiste el `Prestamo` y actualiza el `Libro` en una sola transacción.
4. **Router** — Devuelve la respuesta serializada con `PrestamoResponse`.

---

## 2. Decisiones técnicas

### FastAPI (framework web)

**¿Por qué?**
- **Tipado y validación nativos con Pydantic**: los schemas validan automáticamente los cuerpos de petición y serializan las respuestas. Reduce el código boilerplate y los errores.
- **Documentación automática (OpenAPI/Swagger)**: el endpoint `/docs` se genera sin esfuerzo y permite probar la API interactivamente, lo que aceleró la verificación manual durante el desarrollo.
- **Rendimiento**: basado en Starlette y Uvicorn (ASGI), está entre los frameworks Python más rápidos.
- **Inyección de dependencias** (`Depends(get_db)`): facilita la prueba unitaria sustituyendo dependencias (clave para los tests con SQLite en memoria).
- **Curva de aprendizaje**: muy cercana a Flask, pero con mejores defaults para APIs modernas.

### SQLAlchemy (ORM)

**¿Por qué?**
- **Estándar de facto en Python**: gran comunidad, documentación madura y soporte de la mayoría de motores SQL.
- **Independencia del motor**: la misma capa de modelos funciona en SQLite (desarrollo/pruebas) y en PostgreSQL/MySQL (producción) cambiando solo la URL de conexión.
- **Modelado declarativo claro**: los modelos `Libro` y `Prestamo` son legibles y las relaciones (`relationship`, `ForeignKey`) están explícitas.
- **Integración con Alembic** para migraciones versionadas.
- **Permite SQL crudo** cuando el ORM no es suficiente (escape hatch).

### SQLite (base de datos)

**¿Por qué?**
- **Cero configuración**: un archivo en disco. Perfecto para una prueba técnica, prototipos y desarrollo local.
- **Igual de funcional para el alcance actual**: la API actual no requiere concurrencia masiva, replicación ni características avanzadas.
- **Reproducible**: cualquier persona puede clonar el repo y correr la app sin levantar contenedores ni servicios externos.
- **Excelente para tests**: SQLite en memoria (`sqlite:///:memory:` con `StaticPool`) permite tests aislados y rapidísimos (los 11 tests corren en <0.3s).
- **Migración futura simple**: gracias a SQLAlchemy, pasar a PostgreSQL solo requiere cambiar la URL y la dependencia.

### Stack complementario

| Herramienta | Justificación |
|-------------|---------------|
| **Pydantic v2** | Validación rápida y declarativa de entrada/salida, integración nativa con FastAPI. |
| **Alembic** | Migraciones versionadas; reemplaza a `create_all` para entornos productivos. |
| **Pytest + httpx** | Estándar Python para tests; `httpx` es el cliente HTTP que usa internamente `TestClient` (ASGI nativo). |
| **Uvicorn** | Servidor ASGI rápido recomendado por FastAPI. |
| **UUID en `Prestamo.id`** | Evita colisiones, no expone IDs incrementales y es seguro de generar en cliente sin hablar con la DB. |
| **Enum `EstadoPrestamo`** | Tipado fuerte para el estado (`ACTIVO`/`DEVUELTO`), validado en DB y en Pydantic. |

---

## 3. Herramientas de IA utilizadas

### Claude (Claude Code)

Se utilizó **Claude Code** (Anthropic) como copiloto durante todo el desarrollo del proyecto, en las siguientes tareas:

- **Diseño**: discusión de la estructura de carpetas, separación en capas y elección de patrones (Router → Service → Model).
- **Generación de código**: scaffolding inicial del proyecto, modelos SQLAlchemy, schemas Pydantic, routers FastAPI, capa de servicios, seed de datos y pruebas con pytest.
- **Documentación**: redacción de README.md y este mismo ARCHITECTURE.md.
- **Resolución de problemas**: configuración de credenciales Git/SSH para conectar el repositorio a GitHub.

### Validación manual de los resultados

A pesar del uso de IA, **todo el código generado fue revisado y verificado manualmente** antes de aceptarse:

1. **Revisión de código línea a línea** antes de hacer commit, para asegurar que la lógica reflejara las reglas de negocio reales.
2. **Pruebas funcionales** ejecutando la API con `uvicorn` y probando los endpoints mediante:
   - La UI interactiva de Swagger (`/docs`).
   - Llamadas `curl` y `TestClient` para casos felices y de error (404, 400, etc.).
3. **Suite de tests automatizada** (`pytest tests/ -v`) — 11 pruebas que cubren los flujos principales y los casos de error de cada endpoint. Se ejecutaron después de cada iteración significativa.
4. **Verificación de efectos colaterales**: por ejemplo, después de un `POST /prestamos` se verificó que `ejemplares_disponibles` se decrementara correctamente; después de un `PUT /devolucion`, que se restituyera.
5. **Lectura crítica** de la documentación generada para corregir imprecisiones y adaptar el tono al contexto del proyecto.

> En resumen: la IA aceleró la escritura, pero las decisiones de diseño, la validación de comportamiento y la responsabilidad sobre el resultado final son del autor.

---

## 4. Mejoras pendientes (con estimación de tiempo)

| # | Mejora | Descripción | Estimación |
|---|--------|-------------|------------|
| 1 | **Autenticación JWT** | Endpoint `/auth/login`, generación y verificación de tokens con `python-jose`, dependencia `get_current_user` para proteger rutas. Roles básicos (bibliotecario/usuario). | **4–6 horas** |
| 2 | **Migrar a PostgreSQL con Docker** | `docker-compose.yml` con servicio `db` (Postgres) y `api`. Variable `DATABASE_URL` por entorno. Migraciones Alembic aplicadas en el contenedor al arrancar. | **2–3 horas** |
| 3 | **Cobertura de tests al 100%** | Añadir `pytest-cov`, tests para casos límite (fechas iguales al vencimiento, ISBNs con caracteres especiales, errores de DB) y cobertura del seed y de la capa de modelos. Reporte HTML. | **3–4 horas** |
| 4 | **Notificaciones por vencimiento** | Job programado (APScheduler o cron) que escanea préstamos cuya `fecha_vencimiento` está próxima (e.g. 3 días) y envía email/Slack/notificación. Templates configurables. | **5–8 horas** |
| 5 | **Paginación en endpoints de listado** | Parámetros `?limit=...&offset=...` (o cursor-based) en `GET /prestamos/vencidos`. Respuesta con `items`, `total`, `limit`, `offset`. Modelo Pydantic genérico `Page[T]`. | **2–3 horas** |

**Total estimado: 16 – 24 horas** de trabajo adicional para llevar el proyecto a nivel productivo.

### Otras mejoras consideradas (fuera del alcance solicitado)

- CRUD completo de libros (alta, edición, baja) con permisos por rol.
- Histórico de préstamos por usuario (`GET /usuarios/{id}/prestamos`).
- Métricas y logging estructurado (loguru + Prometheus).
- CI/CD con GitHub Actions: lint (ruff), tests y build automático en cada PR.
- Pre-commit hooks (ruff, mypy, pytest rápido).
