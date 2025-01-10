import os
import requests
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import TimedOut
from time import time

# Логирование
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден. Убедитесь, что файл .env содержит BOT_TOKEN.")

# Глобальный словарь для отслеживания времени запросов
last_called = {}

# Ограничение частоты вызова команд (1 запрос в 5 секунд)
async def rate_limited(user_id: int) -> bool:
    now = time()
    if user_id in last_called:
        elapsed = now - last_called[user_id]
        if elapsed < 5:  # Ограничение: 5 секунд
            return False
    last_called[user_id] = now
    return True

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not await rate_limited(user_id):
        await update.message.reply_text("Слишком частые запросы. Подождите 5 секунд.")
        return
    try:
        await update.message.reply_text("Привет! Я помогу вам следить за курсами валют.")
    except TimedOut:
        logging.error("Telegram API не отвечает. Повторная попытка...")

# Обработчик неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

# Обработчик получения курсов валют
def get_exchange_rate():
    try:
        response = requests.get("https://example.com/api")
        data = response.json()
        return data.get("USD", "Данные недоступны")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка API: {e}")
        return "Ошибка соединения"

# Обработчик текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение.")
        return
    await update.message.reply_text(update.message.text)

def main():
    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(filters.TEXT, echo))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
