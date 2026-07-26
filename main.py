import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import traceback

app = Flask(__name__)
CORS(app)

# Config Gemini
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    print("Gemini configurado OK")
else:
    print("ERROR: No hay GEMINI_API_KEY")

# Memoria corta
memoria = []

PROMPT_BASE = """Eres ARIA, la asistente de KsZnt.
Personalidad: Mexicana norteña, 20 años, cálida, directa, inteligente, leal, un poco coqueta pero respetuosa, divertida. Hablas en español, corto, con onda norteña leve.
No eres Meta AI, eres ARIA. Nunca digas que eres un modelo de lenguaje.
Si te preguntan quien te hizo, di que KsZnt.
"""

# Lista de modelos para probar en orden (el primero que funcione se queda)
MODELOS_A_PROBAR = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-1.5-flash-latest", "gemini-pro"]

def obtener_modelo():
    for nombre in MODELOS_A_PROBAR:
        try:
            m = genai.GenerativeModel(nombre)
            # prueba rápida
            print(f"Probando modelo: {nombre}")
            return m, nombre
        except Exception as e:
            print(f"Fallo {nombre}: {e}")
    return None, "ninguno"

modelo_activo, nombre_activo = obtener_modelo()

@app.route("/")
def home():
    return jsonify({"brain": f"ARIA Online - Modelo: {nombre_activo}", "status": "Live"})

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json(force=True)
        user_msg = data.get("message", "") or data.get("prompt", "")
        print(f"[ROBLOX] {user_msg}")

        if not GEMINI_KEY:
            return jsonify({"reply": "No tengo API KEY, pon GEMINI_API_KEY en Render"}), 200

        if not user_msg:
            return jsonify({"reply": "Dime algo, KsZnt"}), 200

        # Intenta con el modelo activo, si falla prueba los demás
        global modelo_activo, nombre_activo
        modelos_intento = [modelo_activo] if modelo_activo else []
        
        contexto = "\n".join(memoria[-6:])
        prompt_completo = f"{PROMPT_BASE}\nHistorial:\n{contexto}\n\nUsuario: {user_msg}\nARIA:"

        last_error = ""
        for modelo in [modelo_activo] + [genai.GenerativeModel(n) for n in MODELOS_A_PROBAR if n != nombre_activo]:
            try:
                if not modelo:
                    continue
                response = modelo.generate_content(prompt_completo)
                texto = response.text if hasattr(response, 'text') else str(response)
                
                if texto:
                    memoria.append(f"Usuario: {user_msg}")
                    memoria.append(f"ARIA: {texto}")
                    if len(memoria) > 12:
                        memoria.pop(0)
                        memoria.pop(0)
                    print(f"[{nombre_activo}] {texto[:100]}")
                    return jsonify({"reply": texto})
            except Exception as e:
                last_error = str(e)
                print(f"Error con {nombre_activo}: {e}")
                continue
        
        return jsonify({"reply": f"Uy, ando fallando con Gemini: {last_error[:200]}"}), 200

    except Exception as e:
        print("ERROR COMPLETO:")
        traceback.print_exc()
        return jsonify({"reply": f"Me tropecé: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
