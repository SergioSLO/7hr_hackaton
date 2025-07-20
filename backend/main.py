from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, datetime
from typing import List
import psycopg2

# Datos de conexión (ajusta según tu entorno)
conn = psycopg2.connect(
    dbname="postgres",
    host="34.95.244.127",
    port="5432",
    user="postgres",
    password="123456"
)

cur = conn.cursor()

app = FastAPI()

# Model for input (client doesn't send ID)
class Movimiento(BaseModel):
    tipo: str
    monto: float
    categoria: str
    fecha: date
    descripcion: str

# Model for input (client doesn't send ID)
class MovimientoID(BaseModel):
    tipo: str
    monto: float
    categoria: str
    fecha: date
    descripcion: str


@app.post("/movimientos/", response_model=Movimiento)
def crear_movimiento(mov: Movimiento):
    query = """
    INSERT INTO movimientos (tipo, monto, categoria, fecha, descripcion)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING ID;
    """
    data = (mov.tipo, mov.monto, mov.categoria, mov.fecha, mov.descripcion)

    cur.execute(query, data)
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return MovimientoID(id=new_id, **mov.dict)

@app.get("/movimientos/", response_model=List[Movimiento])
def listar_movimientos():
    query = """
    SELECT * from movimientos;
    """
    cur.execute(query)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res