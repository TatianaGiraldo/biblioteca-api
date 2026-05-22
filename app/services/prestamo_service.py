from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import EstadoPrestamo, Libro, Prestamo
from app.schemas.prestamo import PrestamoCreate

DIAS_PRESTAMO = 15


def registrar_prestamo(db: Session, data: PrestamoCreate) -> Prestamo:
    libro = db.query(Libro).filter(Libro.isbn == data.isbn_libro).first()
    if libro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con ISBN '{data.isbn_libro}' no encontrado",
        )
    if libro.ejemplares_disponibles <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay ejemplares disponibles para este libro",
        )

    fecha_prestamo = data.fecha_prestamo or date.today()
    fecha_vencimiento = fecha_prestamo + timedelta(days=DIAS_PRESTAMO)

    prestamo = Prestamo(
        isbn_libro=data.isbn_libro,
        identificacion_usuario=data.identificacion_usuario,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_vencimiento,
        estado=EstadoPrestamo.ACTIVO,
    )
    libro.ejemplares_disponibles -= 1
    db.add(prestamo)
    db.commit()
    db.refresh(prestamo)
    return prestamo


def registrar_devolucion(db: Session, prestamo_id: str) -> Prestamo:
    prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
    if prestamo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo con id '{prestamo_id}' no encontrado",
        )
    if prestamo.estado != EstadoPrestamo.ACTIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El préstamo ya fue devuelto",
        )

    libro = db.query(Libro).filter(Libro.isbn == prestamo.isbn_libro).first()
    if libro is not None:
        libro.ejemplares_disponibles += 1

    prestamo.estado = EstadoPrestamo.DEVUELTO
    db.commit()
    db.refresh(prestamo)
    return prestamo


def listar_vencidos(db: Session) -> list[Prestamo]:
    hoy = date.today()
    return (
        db.query(Prestamo)
        .filter(
            Prestamo.fecha_vencimiento < hoy,
            Prestamo.estado == EstadoPrestamo.ACTIVO,
        )
        .all()
    )
