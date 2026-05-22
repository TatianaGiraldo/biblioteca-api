from pydantic import BaseModel, ConfigDict


class LibroResponse(BaseModel):
    isbn: str
    titulo: str
    area_conocimiento: str
    ejemplares_disponibles: int

    model_config = ConfigDict(from_attributes=True)


class LibroDisponibilidad(BaseModel):
    isbn: str
    titulo: str
    ejemplares_disponibles: int

    model_config = ConfigDict(from_attributes=True)
