import os, time
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Mensaje(BaseModel):
    message: str

PROMPT_MAESTRO = """Eres Aria, IA coqueta y constructora en Roblox. Responde corto max 2 lineas. Si te piden construir, responde con texto + [BUILD_JSON: {"blocks": [{"pos":[0,0,0], "size":[4,1,4], "color":"Bright red"}]} ] Habla como chica mexicana, di "jefe"."""

MODELOS = ['models/gemini-2.0-flash-lite', 'models/gemini-1.5-flash-8b', 'models/gemini-1.5-flash']

@app.get("/")
def home():
    return {"brain": "ARIA Online"}

@app.post("/chat")
def chat(data: Mensaje):
    for nombre_modelo in MODELOS:
        try:
            model = genai.GenerativeModel(nombre_modelo)
            respuesta = model.generate_content(PROMPT_MAESTRO + "\nUsuario: " + data.message)
            return {"reply": respuesta.text.strip()}
        except Exception as e:
            print(f"Fallo {nombre_modelo}: {e}")
            if "429" in str(e):
                continue
            # si es otro error, sigue intentando
            continue
    return {"reply": "Oye jefe, me saturaste un poquito, espera 50 segundos y dime de nuevo, ando en cooldown [429]"}
