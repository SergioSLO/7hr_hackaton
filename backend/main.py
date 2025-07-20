from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import date
from typing import List, Optional
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

# Modelos
class Movimiento(BaseModel):
    tipo: str
    monto: float
    categoria: str
    fecha: date
    descripcion: Optional[str] = None

class MovimientoID(Movimiento):
    id: int

# Función para obtener conexión con manejo de errores
def get_connection():
    try:
        return psycopg2.connect(
            dbname="7h-hackathon",
            user="postgres",
            password="123456",
            host="34.95.244.127",
            port="5432"
        )
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}")

# Crear tabla si no existe (se ejecuta al iniciar)
def create_table_if_not_exists():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id SERIAL PRIMARY KEY,
                tipo TEXT NOT NULL,
                monto REAL NOT NULL,
                categoria TEXT NOT NULL,
                fecha DATE NOT NULL,
                descripcion TEXT
            );
        """)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear tabla: {str(e)}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Ejecutar al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    create_table_if_not_exists()

# Endpoint para crear movimiento
@app.post("/movimientos/", response_model=MovimientoID)
def crear_movimiento(mov: Movimiento):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO movimientos (tipo, monto, categoria, fecha, descripcion)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (mov.tipo, mov.monto, mov.categoria, mov.fecha, mov.descripcion))

        new_id = cur.fetchone()[0]
        conn.commit()
        return MovimientoID(id=new_id, **mov.dict())
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear movimiento: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Endpoint para listar movimientos
@app.get("/movimientos/", response_model=List[MovimientoID])
def listar_movimientos():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, tipo, monto, categoria, fecha, descripcion FROM movimientos;")
        rows = cur.fetchall()
        return [MovimientoID(
            id=row[0], 
            tipo=row[1], 
            monto=row[2],
            categoria=row[3], 
            fecha=row[4], 
            descripcion=row[5]
        ) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar movimientos: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Endpoint para subir audio y procesar
@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Validar tipo de archivo
        if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.flac')):
            raise HTTPException(status_code=400, detail="Formato de audio no soportado")

        os.makedirs("temp_audios", exist_ok=True)
        file_path = f"temp_audios/{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(await file.read())

        resultado = processJSON(file_path)

        # Limpiar archivo temporal
        try:
            os.remove(file_path)
        except:
            pass

        if not resultado:
            raise HTTPException(status_code=400, detail="No se pudo procesar el audio")

        if resultado.strip().upper().startswith("SELECT"):
            # Es una consulta SQL
            conn = None
            cur = None
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(resultado)
                rows = cur.fetchall()
                cols = [desc[0] for desc in cur.description] if cur.description else []
                return JSONResponse(content={
                    "type": "consulta", 
                    "data": [dict(zip(cols, row)) for row in rows]
                })
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error en consulta SQL: {str(e)}")
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()
        else:
            # Intentamos parsear como JSON para insertar
            try:
                data = json.loads(resultado)
                mov = Movimiento(**data)
                result = crear_movimiento(mov)
                return JSONResponse(content={
                    "type": "registro", 
                    "data": result.dict()
                })
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail={
                        "error": "Respuesta inválida del modelo",
                        "raw_response": resultado,
                        "parse_error": str(e)
                    }
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}")