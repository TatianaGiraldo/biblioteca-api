from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.prestamo import EstadoPrestamo


class PrestamoCreate(BaseModel):
    isbn_libro: str
    identificacion_usuario: str
    fecha_prestamo: Optional[date] = None


class PrestamoResponse(BaseModel):
    id: str
    isbn_libro: str
    identificacion_usuario: str
    fecha_prestamo: date
    fecha_vencimiento: date
    estado: EstadoPrestamo

    model_config = ConfigDict(from_attributes=True)
