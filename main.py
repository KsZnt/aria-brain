import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import google.generativeai as genai
import traceback

app = Flask(__name__)
CORS(app)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini configurado OK")
else:
    model = None
    print("ERROR: No hay GEMINI_API_KEY")

memoria = []

PROMPT = "Eres ARIA, asistenta de KsZnt. Mexicana norteña, 20 años, cálida, directa, inteligente, divertida, leal. No eres Meta AI, eres ARIA. Responde corto, en español, con onda norteña pero sin exagerar. Nunca digas que eres un modelo de lenguaje."

@app.route("/")
def home():
    return jsonify({"brain": f"ARIA Online - Gemini {bool(model)}", "status": "Live"})

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json(force=True)
        user_msg = data.get("message", "")
        print(f"[ROBLOX] {user_msg}")

        if not model:
            return jsonify({"reply": "No tengo API KEY configurada, KsZnt revisa el Environment en Render"}), 200

        # Agregamos memoria corta
        memoria.append(f"Usuario: {user_msg}")
        if len(memoria) > 10:
            memoria.pop(0)

        contexto = "\n".join(memoria[-6:])
        prompt_completo = f"{PROMPT}\nHistorial:\n{contexto}\n\nResponde a esto: {user_msg}"

        response = model.generate_content(prompt_completo)
        
        if not response.text:
            return jsonify({"reply": "Me quedé en blanco, repite?"}), 200

        texto = response.text
        memoria.append(f"ARIA: {texto}")
        print(f"[GEMINI] {texto[:100]}")
        return jsonify({"reply": texto})

    except Exception as e:
        print("ERROR COMPLETO:")
        traceback.print_exc()
        return jsonify({"reply": f"Uy, me tropecé un segundo: {e}. Intenta de nuevo."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
