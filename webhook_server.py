import os
import hashlib
import hmac
import base64
from flask import Flask, request, jsonify, Response, stream_with_context
from urllib.parse import quote as url_quote
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "🛰️ Webhook server online..."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    session_id = data.get("session_id", "default-session")

    signed_url_endpoint = "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url"
    headers = {
        "xi-api-key": os.getenv("ELEVENLABS_API_KEY")
    }
    params = {
        "agent_id": os.getenv("ELEVENLABS_AGENT_ID")
    }

    response = requests.get(signed_url_endpoint, headers=headers, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Failed to get signed URL", "details": response.text}), 500

    ws_url = response.json().get("url")
    if not ws_url:
        return jsonify({"error": "No signed URL returned"}), 500

    audio_stream_url = f"{ws_url}&message={url_quote(message)}&session_id={url_quote(session_id)}"

    audio_response = requests.get(audio_stream_url, stream=True)

    def generate():
        for chunk in audio_response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk

    return Response(stream_with_context(generate()), content_type="audio/mpeg")

@app.route("/webhook", methods=["POST"])
def webhook():
    secret = os.getenv("WEBHOOK_SECRET")
    signature = request.headers.get("x-elevenlabs-signature", "")
    body = request.get_data()

    digest = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    computed_signature = base64.b64encode(digest).decode()

    if not hmac.compare_digest(signature, computed_signature):
        return "Invalid signature", 403

    payload = request.get_json()
    print("✅ Webhook received:", payload)

    return "", 204

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)
