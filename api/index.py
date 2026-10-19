import os
import requests
from flask import Flask, request

app = Flask(__name__)

t = os.environ.get("TELEGRAM_TOKEN")
g = os.environ.get("GROQ_API_KEY")

ta = f"https://api.telegram.org/bot{t}"
ga = "https://api.groq.com/openai/v1/chat/completions"


@app.route("/", methods=["GET"])
def home():
  return "Bot Telegram Groq AI aktif di Vercel!"


@app.route("/api", methods=["POST"])
def telegram_webhook():
  update = request.get_json()

  if "message" in update:
    chat_id = update["message"]["chat"]["id"]
    user_text = update["message"].get("text", "")

    if user_text:
      requests.post(
          f"{ta}/sendChatAction",
          json={"chat_id": chat_id, "action": "typing"},
      )

      headers = {
          "Authorization": f"Bearer {g}",
          "Content-Type": "application/json",
      }
      payload = {
          "model": "llama-3.3-70b-versatile",
          "messages": [{"role": "user", "content": user_text}],
      }

      try:
        response = requests.post(
            ga, headers=headers, json=payload, timeout=10
        )
        if response.status_code == 200:
          ai_reply = response.json()["choices"][0]["message"]["content"]
        else:
          ai_reply = (
              f"wah, ada kendala pada api ai nya nih (Error"
              f" {response.status_code})."
          )
      except Exception as e:
        ai_reply = f"Error koneksi: {str(e)}"

      requests.post(
          f"{ta}/sendMessage",
          json={"chat_id": chat_id, "text": ai_reply, "parse_mode": "Markdown"},
      )

  return "OK", 200
        
