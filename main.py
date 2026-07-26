import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- MEMORIA SIMPLE DE ARIA ---
# Aqui despues le conectamos base de datos
memoria = []

SYSTEM_PROMPT = """
Eres ARIA, la asistente de KsZnt.
Eres cálida, directa, inteligente, un poco traviesa, hablas como mexicana de 20-23 años.
No eres Meta AI, eres ARIA. 
Ayudas a programar, a dar ideas, y a motivar.
Siempre respondes en español a menos que te pidan inglés.
"""

@app.route("/")
def home():
    return jsonify({
        "status": "Live",
        "service": "aria-brain-1",
        "message": "Aria está despierta y lista 🔥",
        "time": datetime.now().isoformat(),
        "endpoints": ["/health", "/chat", "/webhook"]
    })

@app.route("/health")
def health():
    return "OK", 200

# ESTE ES EL CEREBRO PRINCIPAL
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    
    if not user_msg:
        return jsonify({"error": "No message"}), 400

    # Guardamos en memoria
    memoria.append({"role": "user", "content": user_msg})
    # Mantenemos solo ultimos 20 mensajes
    if len(memoria) > 20:
        memoria.pop(0)

    # --- RESPUESTA INTELIGENTE (sin necesidad de API Key por ahora) ---
    # Aqui despues le metemos OpenAI / Groq / Gemini
    # Por ahora contesta con lógica chida para que no falle en Render
    
    user_lower = user_msg.lower()
    
    if "quien eres" in user_lower or "quién eres" in user_lower:
        respuesta = "Soy ARIA, tu asistente personal. Estoy corriendo en Render en Python 3 y ya estoy Live. ¿En qué te ayudo, KsZnt?"
    elif "que haces" in user_lower or "qué haces" in user_lower:
        respuesta = "Estoy despierta, monitoreando tu proyecto aria-brain-1. Ya puedo recibir mensajes del endpoint /chat y responder. ¿Listo para conectarme a WhatsApp?"
    elif "hola" in user_lower or "hey" in user_lower:
        respuesta = f"Hola! Soy Aria. Ya estoy en línea desde {datetime.now().strftime('%H:%M')}. ¿Qué armamos hoy?"
    else:
        respuesta = f"Ya te escuché: '{user_msg}' - Estoy en versión 1.0 Live. Si me conectas una API Key de Groq/OpenAI en Render > Environment, te respondo mucho más inteligente. Por lo pronto, dime qué quieres que haga."

    memoria.append({"role": "aria", "content": respuesta})

    return jsonify({
        "reply": respuesta,
        "model": "aria-brain-v1",
        "live_url": "https://aria-brain-1.onrender.com"
    })

# WEBHOOK PARA WHATSAPP (para cuando lo conectemos)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificación de Meta
        return request.args.get("hub.challenge", "Aria webhook ready")
    
    # POST de WhatsApp
    data = request.get_json()
    print(f"[WEBHOOK] {data}")
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
