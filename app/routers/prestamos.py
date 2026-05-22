from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.prestamo import PrestamoCreate, PrestamoResponse
from app.services import prestamo_service

router = APIRouter(prefix="/prestamos", tags=["prestamos"])


@router.post(
    "",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_prestamo(data: PrestamoCreate, db: Session = Depends(get_db)):
    return prestamo_service.registrar_prestamo(db, data)


@router.get("/vencidos", response_model=list[PrestamoResponse])
def listar_vencidos(db: Session = Depends(get_db)):
    return prestamo_service.listar_vencidos(db)


@router.put("/{prestamo_id}/devolucion", response_model=PrestamoResponse)
def registrar_devolucion(prestamo_id: str, db: Session = Depends(get_db)):
    return prestamo_service.registrar_devolucion(db, prestamo_id)
