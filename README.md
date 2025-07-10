# GPT Telegram Bot для отельеров

🧠 Этот бот — персональный помощник по маркетингу и стратегиям в загородных отелях.

## Как запустить

1. Скопируй `.env.example` → `.env` и вставь свои ключи
2. Установи зависимости:
```
pip install -r requirements.txt
```
3. Запусти сервер:
```
python bot.py
```
4. Подключи webhook:
```
https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/setWebhook?url=https://<ТВОЙ_ДОМЕН>.onrender.com
```
