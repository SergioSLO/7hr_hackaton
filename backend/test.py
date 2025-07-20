import io
from pydub import AudioSegment
from google.cloud import speech
from datetime import datetime
import pytz
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.oauth2 import service_account

# Load credentials
credentials = service_account.Credentials.from_service_account_file("h-hackathon-085af3656fa4.json")

# Init Vertex AI
vertexai.init(project="h-hackathon", location="us-central1", credentials=credentials)
print("Loading Gemini model...")
model = GenerativeModel("gemini-2.5-flash")

# Convert M4A to WAV
original_audio = "audio-test-insert-3.m4a"
converted_audio = "converted-audio.wav"
AudioSegment.from_file(original_audio).export(converted_audio, format="wav")

print("Transcribing audio with Google Speech-to-Text...")
client = speech.SpeechClient.from_service_account_file("h-hackathon-085af3656fa4.json")
with io.open(converted_audio, "rb") as audio_file:
    content = audio_file.read()

audio = speech.RecognitionAudio(content=content)
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=48000,
    language_code="es-PE",
    enable_automatic_punctuation=True,
)

response = client.recognize(config=config, audio=audio)
transcript = " ".join([result.alternatives[0].transcript for result in response.results])
print("Transcript:", transcript)

# === Prompt lógico con clasificación y bifurcación ===
# Obtener fecha actual en zona horaria de Perú
tz = pytz.timezone('America/Lima')
fecha_actual = datetime.now(tz).strftime('%Y-%m-%d')

# Construcción del prompt con la fecha actual incorporada
prompt = f"""
Analiza el siguiente mensaje y determina si es:

A) Un *nuevo registro financiero informal*, o  
B) Una *consulta o pregunta sobre los datos registrados*.

### Si es (A), responde solo con el siguiente JSON estricto:
{{
  "tipo": "ingreso" o "egreso",
  "monto": float,
  "categoria": "comida | transporte | servicios | entretenimiento | salud | educación | compras | otros",
  "fecha": "YYYY-MM-DD", // nunca debe ser null
  "descripcion": "texto_original"
}}

Usa reglas inflexibles:
1.⁠ ⁠La moneda siempre es PEN (implícita).
2.⁠ ⁠La fecha debe inferirse del texto. Si no hay, usa hoy ({fecha_actual}).
3.⁠ ⁠Maneja expresiones como:
   - "ayer" → {fecha_actual} - 1 día
   - "hace 3 días" → {fecha_actual} - 3 días
   - "el lunes pasado" → lunes anterior más cercano

### Si es (B), genera un query SQL de lectura para una base de datos relacional con tabla ⁠ movimientos(tipo, monto, categoria, fecha, descripcion) ⁠. La salida debe ser directamente el SQL, sin explicaciones.

Mensaje: {transcript}
"""

try:
    print("Sending prompt...")
    response = model.generate_content(prompt)
    print("✅ Done! Response:")
    print(response.text.strip())
except Exception as e:
    print("❌ Error during model call:")
    print(e)