from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Libro
from app.schemas.libro import LibroDisponibilidad

router = APIRouter(prefix="/libros", tags=["libros"])


@router.get("/{isbn}/disponibilidad", response_model=LibroDisponibilidad)
def consultar_disponibilidad(isbn: str, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.isbn == isbn).first()
    if libro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Libro con ISBN '{isbn}' no encontrado",
        )
    return libro
