from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Webhook está online."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    pergunta = data.get("text", "")

    if not pergunta:
        return jsonify({"error": "Texto não fornecido."}), 400

    resposta = f"Aurora responde: você disse '{pergunta}'"
    return jsonify({"text": resposta})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
