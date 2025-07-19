import os
import datetime
import json
import dateparser
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

# Fecha actual
def obtener_fecha_actual():
    hoy = datetime.date.today()
    dia_semana = hoy.strftime('%A')  # 'Monday', 'Tuesday', ...
    dias_es = {
        "Monday": "lunes",
        "Tuesday": "martes",
        "Wednesday": "miércoles",
        "Thursday": "jueves",
        "Friday": "viernes",
        "Saturday": "sábado",
        "Sunday": "domingo"
    }
    return {
        "fecha": hoy.isoformat(),
        "dia_semana": dias_es.get(dia_semana, dia_semana.lower())
    }

import datetime

# Tool 1: Registrar transacción financiera
def registrar_transaccion(
    tipo: str,
    monto: float,
    categoria: str,
    fecha: str,
    descripcion: str
) -> dict:
    """
    Registra una transacción financiera en formato JSON estricto.

    Puedes usar la herramienta 'calcular_fecha' si el usuario proporciona expresiones como:
    'ayer', 'hace 2 días', 'anteayer', 'el jueves pasado', etc.

    Reglas:
    - 'tipo': 'ingreso' o 'egreso'.
    - 'monto': número en soles (PEN).
    - 'categoria': una de ['comida', 'transporte', 'servicios', 'entretenimiento', 'salud', 'educación', 'compras', 'otros'].
    - 'fecha': formato 'YYYY-MM-DD'.
    - 'descripcion': el texto original provisto por el usuario.
    """
    
    categorias_validas = [
        'comida', 'transporte', 'servicios',
        'entretenimiento', 'salud', 'educación',
        'compras', 'otros'
    ]
    tipo = tipo.lower()
    categoria = categoria.lower()

    if tipo not in {"ingreso", "egreso"}:
        raise ValueError("El tipo debe ser 'ingreso' o 'egreso'")

    if categoria not in categorias_validas:
        print(f"⚠️ Categoría no reconocida: '{categoria}'. Se usará 'otros'.")
        categoria = "otros"

    # Validar fecha
    try:
        datetime.date.fromisoformat(fecha)
    except ValueError:
        raise ValueError("La fecha debe estar en formato 'YYYY-MM-DD'")

    transaccion = {
        "tipo": tipo,
        "monto": float(monto),
        "categoria": categoria,
        "fecha": fecha,
        "descripcion": descripcion
    }

    print("Transacción registrada:", json.dumps(transaccion, ensure_ascii=False, indent=2))
    return transaccion


# === Configurar el modelo Gemini ===
from llama_index.llms.google_genai import GoogleGenAI
from google.genai import types

llm = GoogleGenAI(
    model="gemini-2.5-flash",
    generation_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    ),
)

# === Crear el agente ===
from llama_index.core.agent.workflow import FunctionAgent

system_prompt = f"""
Eres un asistente financiero personal que ayuda a registrar transacciones de ingresos y egresos.
Tu objetivo es entender lenguaje natural relacionado a finanzas personales y convertirlo en una transacción estructurada.
Hoy es {obtener_fecha_actual()["fecha"]}, y el dia es '{obtener_fecha_actual()["dia_semana"]}'.

- Usa la herramienta 'registrar_transaccion' para guardar los datos.

Si el usuario menciona una categoría no reconocida, clasifícala como 'otros' sin hacer preguntas.
Si el usuario no da una fecha explícita ni relativa, asume que se refiere a 'hoy'.

Sé autónomo. No hagas preguntas innecesarias al usuario si puedes resolverlo tú mismo usando las herramientas disponibles.
"""

agent = FunctionAgent(
    tools=[registrar_transaccion],
    llm=llm,
    system_prompt=system_prompt,
)


# === Ejecutar una consulta natural ===
from llama_index.core.agent.workflow import ToolCallResult

async def run_query(texto: str):
    print(f"\n💬 Consulta: {texto}")
    handler = agent.run(texto)
    async for event in handler.stream_events():
        if isinstance(event, ToolCallResult):
            print(f"🔧 Llamó a `{event.tool_name}` con: {event.tool_kwargs}")
        else:
            print(event)
    result = await handler
    print(f"\n🧠 Respuesta final del agente: {result}")
    return result

# === Ejecutar ===
import asyncio

if __name__ == "__main__":
    prompt = "Gasté 20 soles en comida ayer en un almuerzo con amigos"
    prompt = "Gasté en 120 soles en una laptop hace 140 dias"
    asyncio.run(run_query(prompt))