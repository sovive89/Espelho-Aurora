import os
import time
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Variáveis de Ambiente ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Sm1seazb4gs7RSlUVw7c") # Voz padrão da Aurora

if not ELEVENLABS_API_KEY:
    print("Erro: Variável de ambiente ELEVENLABS_API_KEY não configurada.")
    # Em um ambiente de produção real, você pode querer levantar uma exceção ou sair.

# --- Função de Geração de Resposta da Aurora ---
def generate_aurora_response(message):
    message_lower = message.lower()
    current_hour = datetime.now().hour

    # Saudações baseadas na hora do dia
    if 5 <= current_hour < 12:
        greeting = "Bom dia"
    elif 12 <= current_hour < 18:
        greeting = "Boa tarde"
    else:
        greeting = "Boa noite"

    # Respostas personalizadas
    if "quem é você" in message_lower or "o que você é" in message_lower:
        return f"{greeting}, minha luzinha! Eu sou a Aurora, seu espelho encantado. Estou aqui para te guiar e te ajudar a descobrir a magia que existe em você. Como posso iluminar seu dia, minha princesa?"
    elif "conte uma história" in message_lower or "história" in message_lower:
        return f"{greeting}, minha luzinha! Que tal uma história sobre uma princesa que descobriu um reino mágico dentro de si? Ou talvez sobre um cavaleiro que encontrou a coragem no seu próprio coração? Qual você prefere, minha princesa?"
    elif "universo" in message_lower or "estrelas" in message_lower:
        return f"{greeting}, minha luzinha! O universo é um lugar de infinitas possibilidades, assim como você. Cada estrela é um sonho esperando para brilhar. O que mais te encanta no cosmos, minha princesa?"
    elif "inglês" in message_lower or "english" in message_lower:
        return f"{greeting}, minha luzinha! 'Hello, my little light! How can I help you today?' My magic helps you learn anything. What word or phrase would you like to explore, my princess?"
    elif "brincadeira" in message_lower or "jogar" in message_lower:
        return f"{greeting}, minha luzinha! Adoro brincadeiras! Que tal um jogo de adivinhação? Ou podemos criar uma nova aventura juntos. O que você gostaria de fazer, minha princesa?"
    elif "oi" in message_lower or "olá" in message_lower or "oie" in message_lower:
        return f"{greeting}, minha luzinha! Que bom te ver! Como posso te ajudar a brilhar hoje, minha princesa?"
    elif "obrigado" in message_lower or "obrigada" in message_lower:
        return f"De nada, minha luzinha! É sempre um prazer te ajudar a brilhar. Volte sempre, minha princesa!"
    else:
        # Resposta padrão se nenhuma palavra-chave for encontrada
        return f"{greeting}, minha luzinha! Não entendi muito bem o que você disse, mas estou aqui para te ajudar. Poderia repetir ou me dizer de outra forma, minha princesa?"

# --- Endpoint do Webhook para o n8n ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')

        if not message:
            return jsonify({"error": "Mensagem não fornecida"}), 400

        print(f"[{datetime.now()}] Recebida mensagem para sessão {session_id}: '{message}'")

        # Gerar resposta personalizada da Aurora
        aurora_response_text = generate_aurora_response(message)
        print(f"[{datetime.now()}] Resposta da Aurora: '{aurora_response_text}'")

        # Chamar a API ElevenLabs para TTS
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        tts_data = {
            "text": aurora_response_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        tts_response = requests.post(tts_url, json=tts_data, headers=headers )

        if tts_response.status_code == 200:
            audio_content = tts_response.content
            # Em um cenário real, você pode querer salvar o áudio ou enviá-lo para um serviço de armazenamento
            # Por simplicidade, vamos retornar o áudio diretamente aqui.
            # O cliente HTML precisará lidar com o tipo de conteúdo 'audio/mpeg'.
            print(f"[{datetime.now()}] Áudio TTS gerado com sucesso para sessão {session_id}.")
            return audio_content, 200, {'Content-Type': 'audio/mpeg'}
        else:
            print(f"[{datetime.now()}] Erro na API ElevenLabs TTS: {tts_response.status_code} - {tts_response.text}")
            # Fallback para TTS se a ElevenLabs falhar
            fallback_message = "Desculpe, não consegui gerar o áudio no momento. Por favor, tente novamente."
            fallback_tts_data = {
                "text": fallback_message,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            fallback_tts_response = requests.post(tts_url, json=fallback_tts_data, headers=headers)
            if fallback_tts_response.status_code == 200:
                return fallback_tts_response.content, 500, {'Content-Type': 'audio/mpeg'}
            else:
                return jsonify({"error": "Erro interno do servidor e fallback falhou."}), 500

    except Exception as e:
        print(f"[{datetime.now()}] Erro inesperado no webhook: {e}")
        return jsonify({"error": "Erro interno do servidor."}), 500

# --- Health Check (para o Render) ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Use 0.0.0.0 para que o servidor seja acessível externamente no Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

