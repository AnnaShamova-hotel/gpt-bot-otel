import requests
from flask import Flask, request
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

with open("instructions.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

def ask_gpt(user_text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
    return response.json()["choices"][0]["message"]["content"]

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        try:
            reply = ask_gpt(user_text)
        except Exception:
            reply = "Произошла ошибка при обращении к GPT. Попробуй ещё раз позже."
        send_message(chat_id, reply)
    return {"ok": True"}
