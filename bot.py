import requests
from flask import Flask, request
import os
from dotenv import load_dotenv
from collections import defaultdict, deque

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GPT_MODEL = "gpt-4"

# Хранилище истории диалогов (в памяти, по chat_id)
chat_histories = defaultdict(lambda: deque(maxlen=6))

SYSTEM_PROMPT = """
🧭 Твоя роль: стратег, который не продаёт, а формирует влюблённость
Ты — стратег и бренд-директор, который умеет превращать отель в место силы...
(ВСТАВЬ СЮДА ПОЛНОСТЬЮ — вставлено в файле)
"""

def ask_gpt(chat_id, user_text):
    chat = chat_histories[chat_id]
    chat.append({"role": "user", "content": user_text})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(chat)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": GPT_MODEL,
        "messages": messages
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
    reply = response.json()["choices"][0]["message"]["content"]
    chat.append({"role": "assistant", "content": reply})
    return reply

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = str(data["message"]["chat"]["id"])
        user_text = data["message"]["text"]

        if user_text == "/start":
            intro = "Привет. Я помогу тебе увидеть, чем твоё место — не как все. Давай начнём. Расскажи, где находится отель?"
            chat_histories[chat_id].clear()
            chat_histories[chat_id].append({"role": "assistant", "content": intro})
            send_message(chat_id, intro)
        else:
            reply = ask_gpt(chat_id, user_text)
            send_message(chat_id, reply)

    return {"ok": True}