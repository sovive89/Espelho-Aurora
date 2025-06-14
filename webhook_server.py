from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    user_input = data.get("message", "")

    # Aqui você poderia incluir sua lógica com a ElevenLabs ou outro serviço
    resposta = f"Aurora responde: você disse '{user_input}'"

    return jsonify({"response": resposta})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Porta padrão da Render
    app.run(host='0.0.0.0', port=port)
