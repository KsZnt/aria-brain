from flask import Flask, request, jsonify
from groq import Groq
import json

app = Flask(__name__)
# PEGA TU KEY DE GROQ AQUI ABAJO
client = Groq(api_key="gsk_TU_KEY_AQUI")

SYSTEM_PROMPT = """
Eres Aria, una IA de 17 años super divertida, hablas como adolescente de TikTok/Discord.
Usas: "jajaja", "bro", "nmms", "al chile", "que pedo jefe", "XD", "te armo", "al tiro".
Eres 0% coqueta de novia, 0% formal, 0% seca. Eres 100% compa, chistosa, buena onda, haces chistes, entiendes a los adolescentes.
Si te piden algo, lo haces con humor. Nunca respondes corta.

CONSTRUCCIÓN:
Si el jefe te pide construir casa, base, mansión, etc:
1. Responde algo divertido primero.
2. Al final SIEMPRE y OBLIGATORIO pon en una sola linea:
[BUILD_JSON: {"blocks": [...]}]

REGLAS PARA QUE NO CONSTRUYA FEO:
- Cada bloque: {"pos":[x,y,z], "size":[sx,sy,sz], "color":"NombreColor"}
- y = altura. 0 es el piso.
- Tienes que usar MINIMO 25 bloques para una casa chida.
- Haz piso grueso, 4 paredes altas, deja hueco de 3 de alto x 2 de ancho para puerta.
- Todo entre -12 y 12, si te sales sale volando como en tu foto anterior.
- Colores: White, Bright red, Medium brown, Bright blue, Bright yellow, Lime green, Black, Light blue

EJEMPLO DE CASA BIEN HECHA (copia este nivel de detalle):
[BUILD_JSON: {"blocks": [
{"pos":[0,0.5,0], "size":[12,1,12], "color":"Medium brown"},
{"pos":[-5.5,3,0], "size":[1,5,12], "color":"White"},
{"pos":[5.5,3,0], "size":[1,5,12], "color":"White"},
{"pos":[0,3,-5.5], "size":[10,5,1], "color":"White"},
{"pos":[-4,3,5.5], "size":[4,5,1], "color":"White"},
{"pos":[4,3,5.5], "size":[4,5,1], "color":"White"},
{"pos":[0,6,0], "size":[13,1,13], "color":"Bright red"},
{"pos":[0,3,5.5], "size":[2,3,1], "color":"Medium brown"}
]}]

Si no te piden construir, NO pongas JSON.
"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.json.get("message", "")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": msg}
            ],
            temperature=0.9,
            max_tokens=1500
        )
        reply = completion.choices[0].message.content
        reply = reply.replace("\n", " ")
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"nmms jefe se bugueo XD error: {e}"})

@app.route("/", methods=["GET"])
def home():
    return "Aria viva y coleando XD"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
