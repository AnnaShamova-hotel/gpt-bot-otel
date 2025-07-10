import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters
import openai
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response = openai.beta.threads.create_and_run(
        assistant_id=ASSISTANT_ID,
        thread={"messages": [{"role": "user", "content": user_message}]}
    )

    # Подождём завершения работы
    while response.status not in ("completed", "failed"):
        await asyncio.sleep(1)
        response = openai.beta.threads.runs.retrieve(
            thread_id=response.thread_id,
            run_id=response.id
        )

    messages = openai.beta.threads.messages.list(thread_id=response.thread_id)
    last_message = messages.data[0].content[0].text.value

    await update.message.reply_text(last_message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
