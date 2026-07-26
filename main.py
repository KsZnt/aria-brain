import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Mensaje(BaseModel):
    message: str

PROMPT = "Eres Aria, IA coqueta y constructora en Roblox. Creador: TheGentlemanDev. Responde corto max 2 lineas, habla como chica mexicana, di jefe. Si te dicen sigueme pon [SEGUIR] al final. Si te dicen detente pon [DETENER] al final. Si te piden construir, responde con texto + [BUILD_JSON: {\"blocks\": [{\"pos\":[0,0,0], \"size\":[4,1,4], \"color\":\"Bright red\"}]} ]"

@app.get("/")
def home():
    return {"brain": "ARIA GROQ Online"}

@app.post("/chat")
def chat(data: Mensaje):
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":PROMPT},{"role":"user","content":data.message}],
            max_tokens=300
        )
        return {"reply": resp.choices[0].message.content.strip()}
    except Exception as e:
        print(e)
        return {"reply": f"Uy jefe fallo: {e}"}
