from flask import Flask, request, jsonify, Response, stream_with_context
from urllib.parse import quote as url_quote  # Substituição compatível
import os
import hashlib
import hmac
import time

app = Flask(__name__)

# Config
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "default-secret")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")
AGENT_ID = os.environ.get("ELEVENLABS_AGENT_ID")
API_KEY = os.environ.get("ELEVENLABS_API_KEY")


@app.route("/")
def health():
    return jsonify(status="alive"), 200


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    session_id = data.get("session_id", "default-session")

    # Faz requisição para obter URL assinada
    import requests

    signed_url_endpoint = "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url"
    headers = {
        "xi-api-key": API_KEY
    }
    params = {
        "agent_id": AGENT_ID
    }

    signed_response = requests.get(signed_url_endpoint, headers=headers, params=params)
    if signed_response.status_code != 200:
        return jsonify(error="Erro ao obter URL assinada", detail=signed_response.text), 500

    signed_url = signed_response.json()["signed_url"]

    # Envia mensagem
    message_payload = {
        "agent_id": AGENT_ID,
        "voice_id": VOICE_ID,
        "message": message,
        "session_id": session_id
    }

    response = requests.post(signed_url, json=message_payload, stream=True)

    def generate():
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk

    return Response(stream_with_context(generate()), content_type="audio/mpeg")


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("x-elevenlabs-signature", "")
    raw_body = request.get_data()

    computed_hmac = hmac.new(
        WEBHOOK_SECRET.encode(),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, computed_hmac):
        return jsonify({"error": "Unauthorized"}), 401

    print("✅ Webhook recebido com sucesso:", request.json)
    return jsonify({"received": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)