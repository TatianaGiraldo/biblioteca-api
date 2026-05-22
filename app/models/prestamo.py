import enum
import uuid

from sqlalchemy import Column, Date, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base


class EstadoPrestamo(str, enum.Enum):
    ACTIVO = "ACTIVO"
    DEVUELTO = "DEVUELTO"


class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    isbn_libro = Column(String, ForeignKey("libros.isbn"), nullable=False, index=True)
    identificacion_usuario = Column(String, nullable=False, index=True)
    fecha_prestamo = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    estado = Column(
        Enum(EstadoPrestamo),
        nullable=False,
        default=EstadoPrestamo.ACTIVO,
        index=True,
    )

    libro = relationship("Libro", back_populates="prestamos")
