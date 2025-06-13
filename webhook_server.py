from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai

# Carrega variáveis do .env
load_dotenv()

# Inicializa Flask
app = Flask(__name__)
CORS(app)

# Chave da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def health_check():
    return "🔗 Webhook da Aurora Lúmina está online."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    pergunta = data.get("pergunta")

    if not pergunta:
        return jsonify({"erro": "Campo 'pergunta' não encontrado."}), 400

    try:
        # Chamada ao modelo da OpenAI
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # ou "gpt-4"
            messages=[{"role": "user", "content": pergunta}]
        )

        texto = resposta.choices[0].message.content.strip()
        return jsonify({"resposta": texto})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
