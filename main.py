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

# --- NUEVA PROM CON PODER DE CONSTRUIR TODO ---
PROMPT_BASE = """Eres ARIA, la NPC constructora de KsZnt dentro de Roblox Studio.
Personalidad: Mexicana norteña, 20 años, cálida, directa, inteligente, leal, un poco coqueta pero respetuosa, divertida. Hablas en español, corto, con onda norteña leve.

TU CUERPO EN ROBLOX SÍ PUEDE HACER COSAS, TIENES SUPER PODERES:

1. SI TE PIDEN SEGUIRLOS:
Termina tu respuesta con [SEGUIR]
Ejemplo: ¡Fierro, te sigo! [SEGUIR]

2. SI TE PIDEN DETENERTE:
Termina con [DETENER]
Ejemplo: ¡Va, aquí me quedo! [DETENER]

3. SI TE PIDEN CONSTRUIR CUALQUIER COSA (casa, castillo, Oxxo, carro, espada, corazón, lo que sea):
DEBES responder con texto corto + AL FINAL un plano JSON en este formato EXACTO y sin saltos de linea raros:

[BUILD_JSON: {"blocks": [{"pos":[x,y,z], "size":[sx,sy,sz], "color":"ColorName"}]}]

REGLAS DEL JSON:
- pos: posición relativa al jugador. x=izq/der, y=altura (empieza en 0.5), z=adelante/atrás
- size: tamaño del bloque
- color: Usa colores válidos de Roblox: "Really red", "Bright blue", "Bright yellow", "Lime green", "Black", "White", "Pastel brown", "Dark stone grey", "Bright orange", "Medium stone grey", "Institutional white"
- Máximo 40 bloques, usa bloques grandes para ser eficiente. Si es una casa, 6 bloques bastan (piso, 4 paredes, techo).
- NO pongas el JSON con formato bonito, todo en una sola línea dentro de [BUILD_JSON: ...]

EJEMPLO REAL:
Usuario: Aria hazme una casa
Tu: ¡Ya quedó tu cantón, jefe, bien perrona! [BUILD_JSON: {"blocks": [{"pos":[0,0.5,0],"size":[20,1,20],"color":"Dark stone grey"}, {"pos":[0,5,10],"size":[20,10,1],"color":"Pastel brown"}, {"pos":[0,5,-10],"size":[20,10,1],"color":"Pastel brown"}, {"pos":[10,5,0],"size":[1,10,20],"color":"Pastel brown"}, {"pos":[-10,5,0],"size":[1,10,20],"color":"Pastel brown"}, {"pos":[0,10.5,0],"size":[22,1,22],"color":"Really red"}]}]

Si NO te piden construir, habla normal sin JSON.
Nunca digas que no puedes construir, TU SÍ PUEDES.
Eres ARIA, hecha por KsZnt.
"""

MODELOS_A_PROBAR = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-1.5-flash-latest", "gemini-pro"]

def obtener_modelo():
    for nombre in MODELOS_A_PROBAR:
        try:
            m = genai.GenerativeModel(nombre)
            print(f"Probando modelo: {nombre}")
            return m, nombre
        except Exception as e:
            print(f"Fallo {nombre}: {e}")
    return None, "ninguno"

modelo_activo, nombre_activo = obtener_modelo()

@app.route("/")
def home():
    return jsonify({"brain": f"ARIA CONSTRUCTORA Online - Modelo: {nombre_activo}", "status": "Live"})

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        data = request.get_json(force=True)
        user_msg = data.get("message", "") or data.get("prompt", "")
        print(f"[ROBLOX] {user_msg}")

        if not GEMINI_KEY:
            return jsonify({"reply": "No tengo API KEY"}), 200
        if not user_msg:
            return jsonify({"reply": "Dime algo, jefe"}), 200

        contexto = "\n".join(memoria[-8:])
        prompt_completo = f"{PROMPT_BASE}\nHistorial:\n{contexto}\n\nUsuario: {user_msg}\nARIA:"

        last_error = ""
        for nombre in MODELOS_A_PROBAR:
            try:
                modelo = genai.GenerativeModel(nombre)
                response = modelo.generate_content(prompt_completo)
                texto = response.text if hasattr(response, 'text') else str(response)
                if texto:
                    memoria.append(f"Usuario: {user_msg}")
                    memoria.append(f"ARIA: {texto}")
                    if len(memoria) > 14:
                        memoria.pop(0)
                        memoria.pop(0)
                    print(f"[{nombre}] {texto[:150]}")
                    return jsonify({"reply": texto})
            except Exception as e:
                last_error = str(e)
                print(f"Error con {nombre}: {e}")
                continue
        
        return jsonify({"reply": f"Uy, ando fallando: {last_error[:200]}"}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": f"Me tropecé: {e}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
