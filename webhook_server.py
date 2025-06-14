import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Aurora Webhook ativo!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("📩 Payload recebido:", data)

        # Verifica se veio um link de áudio da ElevenLabs
        audio_url = data.get("audio_url")
        texto = data.get("text")
        voice_id = data.get("voice_id")

        if audio_url:
            print(f"🔊 Áudio gerado: {audio_url}")
        if texto:
            print(f"💬 Texto falado: {texto}")
        if voice_id:
            print(f"🗣️ Voice ID: {voice_id}")

        return jsonify({
            "status": "ok",
            "mensagem": "Áudio recebido com sucesso",
            "audio_url": audio_url
        }), 200

    except Exception as e:
        print("❌ Erro:", str(e))
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
