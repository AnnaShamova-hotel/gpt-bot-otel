import os
import logging
from flask import Flask, request
import openai
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")
telegram_token = os.getenv("TELEGRAM_TOKEN")
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, json=data)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Received data: {data}")
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_input = data["message"]["text"]

        try:
            thread = openai.beta.threads.create()
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )
            response = openai.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant_id
            )
            if response.status == "completed":
                messages = openai.beta.threads.messages.list(thread_id=thread.id)
                reply = messages.data[0].content[0].text.value
                send_message(chat_id, reply)
            else:
                send_message(chat_id, "Извини, что-то пошло не так 😢")
        except Exception as e:
            logging.exception("Error processing message")
            send_message(chat_id, "Произошла ошибка 🛠️")

    return "ok"
