import os
import json
import uuid
import base64
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import websocket
from flask_cors import CORS

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Sm1seazb4gs7RSlUVw7c")

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "Olá")
    session_id = data.get("session_id", str(uuid.uuid4()))

    signed_url_endpoint = "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url"
    headers = { "xi-api-key": ELEVENLABS_API_KEY }
    params = { "agent_id": ELEVENLABS_AGENT_ID }

    try:
        signed_url_response = requests.get(signed_url_endpoint, headers=headers, params=params)
        print(f"Status code: {signed_url_response.status_code}")
        print(f"Response text: {signed_url_response.text}")

        if signed_url_response.status_code != 200:
            return jsonify({"error": "Failed to get signed URL", "details": signed_url_response.text}), 500

        signed_url_data = signed_url_response.json()
        ws_url = signed_url_data.get("url")
        if not ws_url:
            return jsonify({"error": "No WebSocket URL in response"}), 500

        ws = websocket.create_connection(ws_url)

        init_message = {
            "type": "conversation_initiation_client_data",
            "conversation_initiation_client_data": {
                "voice_id": ELEVENLABS_VOICE_ID,
                "model_id": "eleven_multilingual_v2",
                "sample_rate": 44100,
                "user_id": session_id
            }
        }

        ws.send(json.dumps(init_message))
        ws.send(json.dumps({
            "type": "user_audio_chunk",
            "user_audio_chunk": {"text": user_message}
        }))

        def generate_audio_stream():
            try:
                while True:
                    message = ws.recv()
                    if not message:
                        break
                    msg_data = json.loads(message)
                    msg_type = msg_data.get("type")

                    if msg_type == "audio":
                        audio_b64 = msg_data["audio_event"].get("audio_base_64")
                        if audio_b64:
                            yield base64.b64decode(audio_b64)
                    elif msg_type == "agent_response" and msg_data["agent_response_event"].get("is_final"):
                        break
            finally:
                ws.close()

        return Response(stream_with_context(generate_audio_stream()), mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received webhook:", json.dumps(data))
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))