import requests
import openai
from flask import Flask, request
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = "asst_fyQfTwvARI3QurpvUTTcPfnW"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Храним thread_id для каждого пользователя
user_threads = {}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def ask_assistant(chat_id, user_text):
    # Получаем или создаем thread_id
    if chat_id not in user_threads:
        thread = openai.beta.threads.create()
        user_threads[chat_id] = thread.id
    thread_id = user_threads[chat_id]

    # Отправляем сообщение пользователю
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_text
    )

    # Запускаем ассистента
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Ждём завершения
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break

    # Получаем ответ
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            return msg.content[0].text.value

    return "Извини, я не смог ответить. Попробуй ещё раз."

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        chat_id = str(data["message"]["chat"]["id"])
        user_text = data["message"]["text"]

        if user_text == "/start":
            greeting = "Привет. Я помогу тебе увидеть, чем твоё место — не как все. Расскажи, где находится отель?"
            send_message(chat_id, greeting)
        else:
            reply = ask_assistant(chat_id, user_text)
            send_message(chat_id, reply)

    return {"ok": True}