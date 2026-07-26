import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

memoria = []

PROMPT = "Eres ARIA, asistente de KsZnt. Mexicana norteña, 20 años, cálida, directa, inteligente, divertida, leal. No eres Meta AI, eres ARIA en Render/Python. Responde en español corto y chido."

@app.route("/")
def home():
    brain = "Conectada a Gemini 🧠" if model else "Sin API Key"
    return jsonify({
        "status": "Live",
        "brain": brain,
        "message": "Aria está despierta y lista 🔥",
        "endpoints": ["/health", "/chat", "/webhook"],
        "time": datetime.now().isoformat()
    })

@app.route("/health")
def health():
    return "OK", 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    msg = data.get("message","").strip()
    if not msg:
        return jsonify({"error":"No message"}),400
    if not model:
        return jsonify({"reply":"No me pusiste la GEMINI_API_KEY en Render > Environment"})

    try:
        hist = "\n".join([f"{m['role']}: {m['content']}" for m in memoria[-10:]])
        full = f"{PROMPT}\nHistorial:\n{hist}\nUsuario: {msg}\nARIA:"
        resp = model.generate_content(full)
        ans = resp.text
        memoria.append({"role":"user","content":msg})
        memoria.append({"role":"aria","content":ans})
        if len(memoria)>20:
            memoria.pop(0)
        return jsonify({"reply": ans})
    except Exception as e:
        return jsonify({"reply": f"Error: {e}"}),500

@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method=="GET":
        return request.args.get("hub.challenge","Aria webhook ready")
    return jsonify({"status":"received"}),200

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
