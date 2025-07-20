from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # Guardamos el archivo temporalmente
    contents = await file.read()
    file_location = f"temp_audios/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(contents)

    # Aquí podrías procesar el audio si quieres (ej. reconocimiento de voz, etc.)

    return JSONResponse(content={"message": "Audio recibido correctamente", "filename": file.filename})
