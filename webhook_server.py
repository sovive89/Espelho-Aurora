from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import json
import websocket
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

XI_API_KEY = os.getenv("XI_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Texto não fornecido"}), 400

    text = data["text"]
    audio_bytes = stream_audio(text)
    if not audio_bytes:
        return jsonify({"error": "Falha ao gerar áudio"}), 500

    return send_file(BytesIO(audio_bytes), mimetype="audio/mpeg")

def stream_audio(text):
    url = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input"
    headers = {
        "xi-api-key": XI_API_KEY,
        "Content-Type": "application/json"
    }

    audio_buffer = BytesIO()

    def on_open(ws):
        message = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        ws.send(json.dumps(message))

    def on_message(ws, message):
        try:
            msg = json.loads(message)
            if "audio" in msg:
                chunk = bytes.fromhex(msg["audio"])
                audio_buffer.write(chunk)
        except Exception as e:
            print("Erro ao processar chunk:", e)

    def on_error(ws, error):
        print("Erro no WebSocket:", error)

    ws = websocket.WebSocketApp(
        url,
        header=[f"{k}: {v}" for k, v in headers.items()],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error
    )

    ws.run_forever()
    return audio_buffer.getvalue()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
