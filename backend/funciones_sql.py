import psycopg2
import psycopg2
from decimal import Decimal
import datetime

def ejecutar_query(query: str):
    try:
        conn = psycopg2.connect(
            dbname="7h-hackathon",
            host="34.95.244.127",
            port="5432",
            user="postgres",
            password="123456"
        )
        cur = conn.cursor()

        cur.execute(query)
        rows = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]

        resultado_formateado = []
        for row in rows:
            fila_dict = {}
            for i, valor in enumerate(row):
                # Convertir Decimal y fecha a tipos nativos compatibles con JSON
                if isinstance(valor, Decimal):
                    valor = float(valor)
                elif isinstance(valor, (datetime.date, datetime.datetime)):
                    valor = valor.isoformat()
                fila_dict[columnas[i]] = valor
            resultado_formateado.append(fila_dict)

        return resultado_formateado

    except Exception as e:
        return {"error": str(e)}

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

print(ejecutar_query("SELECT SUM(monto) FROM movimientos WHERE tipo = 'Egreso' AND fecha BETWEEN '2010-07-07' AND '2025-07-13';"))

print(ejecutar_query("SELECT * FROM movimientos;"))