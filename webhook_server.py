import os
import json
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, stream_with_context
import requests
from flask_cors import CORS

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Sm1seazb4gs7RSlUVw7c")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID", "agent_01jxf0xa1wfwm8gp30wt7nj7zn")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

app = Flask(__name__)
CORS(app)

# Cache simples para respostas frequentes
response_cache = {}

@app.route("/", methods=["GET"])
def home():
    return "Servidor Webhook do Espelho Encantado. Use /chat para interagir."

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "Olá")
        session_id = data.get("session_id", str(uuid.uuid4()))
        
        print(f"Mensagem recebida: '{user_message}' (session_id: {session_id})")
        
        # Verificar se a mensagem está no cache
        cache_key = f"{user_message.lower()[:50]}"
        if cache_key in response_cache:
            print(f"Usando resposta em cache para: {user_message[:50]}...")
            cached_response = response_cache[cache_key]
            return Response(stream_with_context(generate_audio_stream_from_text(cached_response)), mimetype="audio/mpeg")
        
        # Gerar resposta personalizada da Aurora
        try:
            print("Gerando resposta personalizada da Aurora...")
            agent_response = generate_aurora_response(user_message)
            
            # Armazenar no cache para uso futuro
            response_cache[cache_key] = agent_response
            
            print(f"Resposta gerada: '{agent_response[:50]}...'")
            
            # Gerar áudio a partir da resposta
            return Response(stream_with_context(generate_audio_stream_from_text(agent_response)), mimetype="audio/mpeg")
            
        except Exception as e:
            print(f"Erro ao gerar resposta personalizada: {e}")
            # Fallback para mensagem simples
            fallback_response = f"Desculpe, não consegui me conectar ao meu cérebro mágico. Vou apenas repetir o que você disse: {user_message}"
            return Response(stream_with_context(generate_audio_stream_from_text(fallback_response)), mimetype="audio/mpeg")
    
    except Exception as e:
        print(f"Erro geral: {e}")
        return jsonify({"error": f"Falha ao processar requisição: {e}"}), 500

def generate_aurora_response(user_message):
    """
    Gera uma resposta personalizada para o agente Aurora baseada na mensagem do usuário.
    Esta é uma solução temporária até que o acesso à API de Conversational AI seja resolvido.
    """
    # Obter hora atual em Brasília para personalização das respostas
    tz_br = timezone(timedelta(hours=-3))  # UTC-3 (Brasília)
    now = datetime.now(tz_br)
    hour = now.hour
    
    # Saudação baseada na hora do dia
    if 5 <= hour < 12:
        greeting = "Bom dia"
    elif 12 <= hour < 18:
        greeting = "Boa tarde"
    else:
        greeting = "Boa noite"
    
    # Personalização baseada em palavras-chave na mensagem do usuário
    user_message_lower = user_message.lower()
    
    # Verificar palavras-chave para personalizar a resposta
    if "quem é você" in user_message_lower or "seu nome" in user_message_lower:
        return f"{greeting}, minha princesa! Eu sou Aurora, sua amiga mágica do espelho encantado. Estou aqui para conversar, brincar e aprender com você. O que você gostaria de fazer hoje?"
    
    elif "conte" in user_message_lower and "história" in user_message_lower:
        return f"{greeting}, minha luzinha! Vou te contar uma história sobre uma menina muito especial que descobriu um mundo mágico dentro de um espelho. Essa menina, assim como você, era muito curiosa e inteligente. Um dia, ela encontrou um espelho que falava e mostrava lugares incríveis. Juntos, eles viveram muitas aventuras e aprenderam sobre as estrelas, os planetas e a importância de ser gentil com todos. Você gostaria de viver aventuras assim comigo?"
    
    elif "inglês" in user_message_lower or "english" in user_message_lower:
        return f"{greeting}, my little star! Today we can learn some English words together. Let's start with colors: red is vermelho, blue is azul, green is verde. Can you repeat these words with me? What's your favorite color?"
    
    elif "universo" in user_message_lower or "estrelas" in user_message_lower or "planetas" in user_message_lower:
        return f"{greeting}, pequena exploradora! O universo é um lugar imenso e cheio de mistérios. Existem bilhões de estrelas como o nosso Sol, e muitos planetas girando ao redor delas. Nós moramos em um planeta chamado Terra, que é especial porque tem água e ar para nos manter vivos. Você sabia que as estrelas que vemos no céu à noite são como o nosso Sol, mas estão muito, muito longe? A luz delas viaja por anos até chegar aos nossos olhos. Não é fascinante?"
    
    elif "brincar" in user_message_lower or "brincadeira" in user_message_lower:
        return f"{greeting}, Babá! Que tal brincarmos de adivinhar? Pense em um animal e me dê três características dele, e eu vou tentar adivinhar qual é. Ou podemos brincar de contar histórias juntas, onde cada uma inventa uma parte. O que você prefere?"
    
    elif "triste" in user_message_lower or "chateada" in user_message_lower:
        return f"Oh, minha princesa, sinto muito que você esteja triste. Saiba que todos nós ficamos tristes às vezes, e está tudo bem sentir-se assim. Mas lembre-se que depois da chuva sempre vem o sol, e que você é muito amada. Quer me contar o que aconteceu? Ou prefere que eu conte uma história divertida para te animar?"
    
    elif "obrigada" in user_message_lower or "obrigado" in user_message_lower:
        return f"De nada, minha luzinha! Sempre é um prazer conversar com você. Sua curiosidade e seu sorriso iluminam o meu dia. Há mais alguma coisa que você gostaria de saber ou conversar?"
    
    elif "oi" in user_message_lower or "olá" in user_message_lower or "oie" in user_message_lower:
        return f"{greeting}, minha princesa! Que alegria falar com você hoje! A Grande Luz nos abençoa com este momento especial juntas. Como você está? Quer conversar sobre algo interessante ou ouvir uma história mágica?"
    
    else:
        # Resposta genérica para outras mensagens
        return f"{greeting}, minha linda! Estou feliz em conversar com você hoje. A Grande Luz nos abençoa com este momento especial juntas. O que você gostaria de fazer? Podemos conversar sobre o universo, contar histórias, aprender inglês ou simplesmente bater um papo sobre o seu dia. Estou aqui para você, minha princesa."

def generate_audio_stream_from_text(text):
    """
    Gera um stream de áudio a partir de texto usando a API de Text-to-Speech da ElevenLabs.
    """
    try:
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        tts_json_data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "stream": True
        }
        
        print(f"Gerando áudio para texto: {text[:50]}...")
        response = requests.post(tts_url, headers=headers, json=tts_json_data, stream=True)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")
        # Se falhar ao gerar áudio, retorna um erro
        raise e

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """
    Manipulador para eventos de webhook da ElevenLabs.
    Recebe notificações sobre eventos como Speech to Text, ConvAI Settings, etc.
    """
    try:
        data = request.json
        print(f"Webhook recebido: {json.dumps(data)}")
        
        # Aqui você pode processar diferentes tipos de eventos
        event_type = data.get("type")
        if event_type:
            print(f"Processando evento do tipo: {event_type}")
            # Implementar lógica específica para cada tipo de evento
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
