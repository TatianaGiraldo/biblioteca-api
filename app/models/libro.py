from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Libro(Base):
    __tablename__ = "libros"

    isbn = Column(String, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    area_conocimiento = Column(String, nullable=False, index=True)
    ejemplares_disponibles = Column(Integer, nullable=False, default=0)

    prestamos = relationship("Prestamo", back_populates="libro")
