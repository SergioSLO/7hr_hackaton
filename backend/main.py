from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, datetime


app = FastAPI()

# Modelo para recibir datos
class Movimientos(BaseModel):
    id: int
    tipo: str
    monto: float
    categoria: str
    fecha: date
    descripcion: str

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Endpoint con parámetro en la ruta
@app.get("/movimientos/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

# Endpoint POST con cuerpo
@app.post("/items/")
def create_item(item: Item):
    return {"received_item": item}