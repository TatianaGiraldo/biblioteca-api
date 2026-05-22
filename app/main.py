from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, SessionLocal, engine
from app.models import Libro, Prestamo  # noqa: F401  (registra los modelos en Base.metadata)
from app.routers import libros, prestamos
from app.seed import seed_libros


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_libros(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Biblioteca API", lifespan=lifespan)
app.include_router(libros.router)
app.include_router(prestamos.router)


@app.get("/")
def root():
    return {"message": "Biblioteca API"}
