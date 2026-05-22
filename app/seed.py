from sqlalchemy.orm import Session

from app.models import Libro

LIBROS_SEED = [
    {"isbn": "978-0132350884", "titulo": "Clean Code", "area_conocimiento": "Ingeniería de Software", "ejemplares_disponibles": 3},
    {"isbn": "978-0201633610", "titulo": "Design Patterns", "area_conocimiento": "Ingeniería de Software", "ejemplares_disponibles": 2},
    {"isbn": "978-0262033848", "titulo": "Introduction to Algorithms", "area_conocimiento": "Ciencias de la Computación", "ejemplares_disponibles": 4},
    {"isbn": "978-0131103627", "titulo": "The C Programming Language", "area_conocimiento": "Ciencias de la Computación", "ejemplares_disponibles": 2},
    {"isbn": "978-8437604947", "titulo": "Don Quijote de la Mancha", "area_conocimiento": "Literatura", "ejemplares_disponibles": 5},
    {"isbn": "978-0307474728", "titulo": "Cien años de soledad", "area_conocimiento": "Literatura", "ejemplares_disponibles": 4},
    {"isbn": "978-0307408877", "titulo": "La sombra del viento", "area_conocimiento": "Literatura", "ejemplares_disponibles": 3},
    {"isbn": "978-0062316097", "titulo": "Sapiens: De animales a dioses", "area_conocimiento": "Historia", "ejemplares_disponibles": 3},
    {"isbn": "978-8499926513", "titulo": "Una breve historia del tiempo", "area_conocimiento": "Física", "ejemplares_disponibles": 2},
    {"isbn": "978-0140439120", "titulo": "El origen de las especies", "area_conocimiento": "Biología", "ejemplares_disponibles": 2},
    {"isbn": "978-0374533557", "titulo": "Pensar rápido, pensar despacio", "area_conocimiento": "Psicología", "ejemplares_disponibles": 3},
    {"isbn": "978-1305585096", "titulo": "Cálculo: trascendentes tempranas", "area_conocimiento": "Matemáticas", "ejemplares_disponibles": 4},
    {"isbn": "978-0073383095", "titulo": "Álgebra lineal", "area_conocimiento": "Matemáticas", "ejemplares_disponibles": 3},
    {"isbn": "978-1305585126", "titulo": "Principios de Economía", "area_conocimiento": "Economía", "ejemplares_disponibles": 2},
    {"isbn": "978-0133804461", "titulo": "Macroeconomía", "area_conocimiento": "Economía", "ejemplares_disponibles": 2},
    {"isbn": "978-0323393041", "titulo": "Anatomía de Gray", "area_conocimiento": "Medicina", "ejemplares_disponibles": 1},
    {"isbn": "978-1119316152", "titulo": "Química orgánica", "area_conocimiento": "Química", "ejemplares_disponibles": 2},
    {"isbn": "978-0140449334", "titulo": "El arte de la guerra", "area_conocimiento": "Filosofía", "ejemplares_disponibles": 5},
    {"isbn": "978-8420674278", "titulo": "Meditaciones", "area_conocimiento": "Filosofía", "ejemplares_disponibles": 3},
    {"isbn": "978-0134685991", "titulo": "Effective Java", "area_conocimiento": "Ingeniería de Software", "ejemplares_disponibles": 2},
]


def seed_libros(db: Session) -> None:
    if db.query(Libro).count() > 0:
        return
    db.add_all(Libro(**data) for data in LIBROS_SEED)
    db.commit()
