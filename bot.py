import os
import logging
import asyncio
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import openai

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение ключей из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_fyQfTwvARI3QurpvUTTcPfnW"  # ← Твой кастомный ассистент

openai.api_key = OPENAI_API_KEY

# Создание потока общения для каждого пользователя
user_threads = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я здесь, чтобы помочь тебе переосмыслить и усилить твой отель. Расскажи, с чего начнём?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_message = update.message.text

    if user_id not in user_threads:
        thread = openai.beta.threads.create()
        user_threads[user_id] = thread.id
    else:
        thread = openai.beta.threads.retrieve(user_threads[user_id])

    # Добавить сообщение пользователя в поток
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # Запустить ассистента на потоке
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )

    # Ожидание завершения run
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            await update.message.reply_text("Произошла ошибка при общении с GPT. Попробуй ещё раз позже.")
            return
        await asyncio.sleep(1)

    # Получить ответ
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    assistant_response = next((msg.content[0].text.value for msg in reversed(messages.data) if msg.role == "assistant"), None)

    if assistant_response:
        await update.message.reply_text(assistant_response)
    else:
        await update.message.reply_text("Что-то пошло не так. Попробуй ещё раз.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()
