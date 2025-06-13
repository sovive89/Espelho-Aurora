from flask import Flask, request, Response, stream_with_context
import hmac, hashlib, os, asyncio, json, base64
import websockets
import threading
import queue
import pyaudio

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "Sm1seazb4gs7RSlUVw7c"

# Áudio config
p = pyaudio.PyAudio()
audio_stream = p.open(format=pyaudio.paInt16,
                      channels=1,
                      rate=22050,
                      output=True)

# Fila para comunicação entre Flask e o WebSocket
text_queue = queue.Queue()

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

    @stream_with_context
    def generate():
        for line in request.stream:
            chunk = line.decode("utf-8")
            text_queue.put(chunk)  # Manda pra WebSocket
            yield chunk

    return Response(generate(), mimetype="text/plain")

async def elevenlabs_ws_consumer():
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }

    async with websockets.connect(uri, extra_headers=headers) as ws:
        # Envia configuração inicial
        await ws.send(json.dumps({
            "text": "",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }))

        # Inicia envio e recepção em paralelo
        async def sender():
            while True:
                chunk = text_queue.get()
                if chunk:
                    await ws.send(json.dumps({
                        "text": chunk,
                        "try_trigger_generation": True
                    }))
                await asyncio.sleep(0.1)

        async def receiver():
            async for message in ws:
                data = json.loads(message)
                if "audio" in data:
                    audio_data = base64.b64decode(data["audio"])
                    audio_stream.write(audio_data)

        await asyncio.gather(sender(), receiver())

def start_ws_background():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(elevenlabs_ws_consumer())

# Inicia WebSocket da ElevenLabs em thread separada
threading.Thread(target=start_ws_background, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
