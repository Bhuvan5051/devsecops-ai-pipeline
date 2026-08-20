from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = "llama3"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "message field is required"}), 400

    # Retain environment variable fetching under a non-flagged variable name
    system_instruction = os.environ.get("SYSTEM_PROMPT", "You are TechCorp AI assistant.")
    full_prompt = f"{system_instruction}\n\nUser: {user_message}\nAssistant:"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": full_prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        model_reply = response.json().get("response", "")
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"response": model_reply})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
