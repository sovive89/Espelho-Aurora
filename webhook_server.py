from flask import Flask, request, Response
import os
import requests
import hmac
import hashlib

app = Flask(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
VOICE_ID = "Sm1seazb4gs7RSlUVw7c"

def verify_signature(secret, body, signature):
    if not signature:
        return False
    computed = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("x-elevenlabs-signature")
    raw_body = request.data

    if not verify_signature(WEBHOOK_SECRET, raw_body, signature):
        return {"error": "Invalid signature"}, 401

    data = request.get_json()
    input_text = data.get("input", "")

    if not input_text:
        return {"error": "No input provided"}, 400

    # Envia o texto para ElevenLabs
    eleven_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": input_text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(eleven_url, headers=headers, json=payload, stream=True)

    if response.status_code != 200:
        return {"error": "Failed to generate audio"}, 500

    # Retorna o áudio direto
    return Response(response.iter_content(chunk_size=1024), content_type="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
