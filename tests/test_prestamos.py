from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import EstadoPrestamo, Libro, Prestamo


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add_all([
        Libro(isbn="TEST-001", titulo="Libro Test", area_conocimiento="Pruebas", ejemplares_disponibles=2),
        Libro(isbn="TEST-002", titulo="Libro Agotado", area_conocimiento="Pruebas", ejemplares_disponibles=0),
    ])
    db.commit()

    yield db, TestingSessionLocal

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    _, TestingSessionLocal = test_db

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- GET /libros/{isbn}/disponibilidad ---

def test_disponibilidad_ok(client):
    r = client.get("/libros/TEST-001/disponibilidad")
    assert r.status_code == 200
    assert r.json() == {
        "isbn": "TEST-001",
        "titulo": "Libro Test",
        "ejemplares_disponibles": 2,
    }


def test_disponibilidad_libro_no_existe(client):
    r = client.get("/libros/NOEXISTE/disponibilidad")
    assert r.status_code == 404
    assert "no encontrado" in r.json()["detail"]


# --- POST /prestamos ---

def test_registrar_prestamo_ok(client):
    r = client.post("/prestamos", json={
        "isbn_libro": "TEST-001",
        "identificacion_usuario": "CC123",
        "fecha_prestamo": "2026-05-22",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["estado"] == "ACTIVO"
    assert data["fecha_prestamo"] == "2026-05-22"
    assert data["fecha_vencimiento"] == "2026-06-06"  # +15 días
    assert data["isbn_libro"] == "TEST-001"
    assert "id" in data

    # Ejemplar decrementado
    r = client.get("/libros/TEST-001/disponibilidad")
    assert r.json()["ejemplares_disponibles"] == 1


def test_registrar_prestamo_fecha_default_hoy(client):
    r = client.post("/prestamos", json={
        "isbn_libro": "TEST-001",
        "identificacion_usuario": "CC123",
    })
    assert r.status_code == 201
    assert r.json()["fecha_prestamo"] == date.today().isoformat()


def test_registrar_prestamo_libro_no_existe(client):
    r = client.post("/prestamos", json={
        "isbn_libro": "NOEXISTE",
        "identificacion_usuario": "CC123",
    })
    assert r.status_code == 404


def test_registrar_prestamo_sin_ejemplares(client):
    r = client.post("/prestamos", json={
        "isbn_libro": "TEST-002",
        "identificacion_usuario": "CC123",
    })
    assert r.status_code == 400
    assert "No hay ejemplares" in r.json()["detail"]


# --- PUT /prestamos/{id}/devolucion ---

def test_devolucion_ok(client):
    r = client.post("/prestamos", json={
        "isbn_libro": "TEST-001",
        "identificacion_usuario": "CC123",
    })
    prestamo_id = r.json()["id"]

    r = client.put(f"/prestamos/{prestamo_id}/devolucion")
    assert r.status_code == 200
    assert r.json()["estado"] == "DEVUELTO"

    # Ejemplar restituido
    r = client.get("/libros/TEST-001/disponibilidad")
    assert r.json()["ejemplares_disponibles"] == 2


def test_devolucion_no_existe(client):
    r = client.put("/prestamos/00000000-0000-0000-0000-000000000000/devolucion")
    assert r.status_code == 404


def test_devolucion_ya_devuelto(client):
    r = client.post("/prestamos", json={
        "isbn_libro": "TEST-001",
        "identificacion_usuario": "CC123",
    })
    prestamo_id = r.json()["id"]

    client.put(f"/prestamos/{prestamo_id}/devolucion")
    r = client.put(f"/prestamos/{prestamo_id}/devolucion")
    assert r.status_code == 400
    assert "ya fue devuelto" in r.json()["detail"]


# --- GET /prestamos/vencidos ---

def test_vencidos_vacio(client):
    r = client.get("/prestamos/vencidos")
    assert r.status_code == 200
    assert r.json() == []


def test_vencidos_con_datos(client, test_db):
    db, _ = test_db
    db.add(Prestamo(
        isbn_libro="TEST-001",
        identificacion_usuario="CC999",
        fecha_prestamo=date(2026, 1, 1),
        fecha_vencimiento=date(2026, 1, 16),
        estado=EstadoPrestamo.ACTIVO,
    ))
    db.add(Prestamo(
        isbn_libro="TEST-001",
        identificacion_usuario="CC888",
        fecha_prestamo=date(2026, 1, 1),
        fecha_vencimiento=date(2026, 1, 16),
        estado=EstadoPrestamo.DEVUELTO,
    ))
    db.commit()

    r = client.get("/prestamos/vencidos")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["identificacion_usuario"] == "CC999"
    assert data[0]["estado"] == "ACTIVO"
