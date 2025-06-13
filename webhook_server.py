import asyncio
import websockets
import json
import base64
import numpy as np
import sounddevice as sd
import os

VOICE_ID = "Sm1seazb4gs7RSlUVw7c"
API_KEY = os.getenv("ELEVENLABS_API_KEY")  # ou cole direto

samplerate = 22050

async def speak_streamed_text(text_chunks):
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input"
    headers = { "xi-api-key": API_KEY }

    async with websockets.connect(uri, extra_headers=headers) as ws:
        await ws.send(json.dumps({
            "text": "",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }))

        async def send_chunks():
            for chunk in text_chunks:
                await ws.send(json.dumps({
                    "text": chunk,
                    "try_trigger_generation": True
                }))
                await asyncio.sleep(0.1)

        async def receive_audio():
            async for message in ws:
                data = json.loads(message)
                if "audio" in data:
                    audio_bytes = base64.b64decode(data["audio"])
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
                    sd.play(audio_np, samplerate=samplerate)
                    sd.wait()

        await asyncio.gather(send_chunks(), receive_audio())

# Exemplo
if __name__ == "__main__":
    chunks = [
        "Olá, ", "eu sou a Aurora. ",
        "Estou aqui pra ajudar. ", 
        "O que deseja saber hoje?"
    ]
    asyncio.run(speak_streamed_text(chunks))
