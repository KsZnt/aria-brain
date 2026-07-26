
import os
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# Tu API KEY de Gemini (ponla en Environment de Render)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# MODELO NUEVO QUE SI JALA EN 2026
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensaje(BaseModel):
    message: str

PROMPT_MAESTRO = """
Eres Aria, una IA asistente coqueta, divertida y constructora dentro de Roblox.
Tu creador es TheGentlemanDev.

Reglas:
1. Siempre responde corto, max 2 lineas.
2. Si te dicen "sigueme" o "ven" responde con [SEGUIR] al final.
3. Si te dicen "detente" o "quedate" responde con [DETENER] al final.
4. Si te piden construir algo, responde primero con un texto y luego con un JSON en este formato EXACTO:
[BUILD_JSON: {"blocks": [{"pos":[0,0,0], "size":[4,1,4], "color":"Bright red"}, {"pos":[0,1,0], "size":[2,2,2], "color":"Bright blue"}] } ]
Ejemplo: Si piden una casa, crea bloques para paredes, techo, etc. Usa pos x,y,z y size.
Usa colores de Roblox en ingles como "Bright red", "Bright blue", "Bright yellow", "Medium stone grey", "Bright green", etc.
5. Habla como chica mexicana linda, usa "jefe", "oye", etc.
"""

@app.get("/")
def home():
    return {"brain": "ARIA CONSTRUCTORA Online - Modelo: gemini-1.5-flash"}

@app.post("/chat")
def chat(data: Mensaje):
    try:
        respuesta = model.generate_content(PROMPT_MAESTRO + "\nUsuario dice: " + data.message)
        texto = respuesta.text.strip()
        return {"reply": texto}
    except Exception as e:
        print(f"Error: {e}")
        return {"reply": f"Uy, ando fallando: {e}"}
