# Обработчик команды /start

from time import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut
import logging

# Глобальный словарь для ограничения частоты запросов
last_called = {}

# Ограничение частоты вызова команд (1 запрос в 5 секунд)
async def rate_limited(user_id: int) -> bool:
    now = time()
    if user_id in last_called:
        elapsed = now - last_called[user_id]
        if elapsed < 3:  # Ограничение: 3 секунды
            return False
    last_called[user_id] = now
    return True

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_first_name = update.message.from_user.first_name
    if not await rate_limited(user_id):
        await update.message.reply_text("Слишком частые запросы. Подождите 3 секунды перед следующим запросом.")
        return
    try:
        await update.message.reply_text(f"Привет, {user_first_name}! Я помогу следить за курсами валют.")
    except TimedOut:
        logging.error("Telegram API не отвечает. Повторная попытка...")
