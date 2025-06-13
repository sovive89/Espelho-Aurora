import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from websocket import create_connection

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurações (use seu modelo e voz específicos)
ELEVENLABS_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "Sm1seazb4gs7RSlUVw7c")  # default ou defina no .env

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    try:
        data = request.get_json()
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Texto não encontrado."}), 400

        # Conexão WebSocket com ElevenLabs
        ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input"
        ws_headers = {
            "xi-api-key": ELEVENLABS_API_KEY
        }

        ws = create_connection(ws_url, header=[f"xi-api-key: {ELEVENLABS_API_KEY}"])

        # Envia instruções iniciais
        ws.send('{"text": "' + text + '", "model_id": "eleven_multilingual_v2"}')

        # Recebe os dados de áudio (streaming)
        audio_data = b""
        while True:
            chunk = ws.recv()
            if isinstance(chunk, bytes):
                audio_data += chunk
            elif '"audio"' in chunk:
                break

        ws.close()

        # Retorna o áudio como base64 (ou salve e envie um link se preferir)
        from base64 import b64encode
        encoded_audio = b64encode(audio_data).decode("utf-8")

        return jsonify({
            "audio_base64": encoded_audio,
            "message": "Stream recebido com sucesso."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
