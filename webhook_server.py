from flask import Flask, request, jsonify, Response, stream_with_context
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

@app.route("/", methods=["GET"])
def index():
    return "🔥 Espelho Aurora rodando com sucesso!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("x-elevenlabs-signature")
    raw_body = request.data

    # Verificação HMAC
    if not verify_signature(WEBHOOK_SECRET, raw_body, signature):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.json
    print("📩 Evento recebido:", event)
    return jsonify({"status": "ok"}), 200

def verify_signature(secret, body, signature):
    if not signature:
        return False
    computed = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
