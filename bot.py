from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config.config import TOKEN
from handlers.start_handler import start
from handlers.help_handler import help_command
from utils.logger import logger
from handlers.currency_handler import currencies_all, currency_today
from handlers.rate_handler import rate, rate_on_date, echo, unknown
from db import execute_query
import re

def get_currency_codes():
    """
    Загружает список доступных валют из БД (таблица currency_requests).
    """
    try:
        query = "SELECT DISTINCT currency_code FROM currency_requests"
        results = execute_query(query)
        return {row[0] for row in results}
    except Exception as e:
        logger.error(f"[BOT] Ошибка загрузки валют из БД: {e}")
        return set()

async def is_currency_command(update):
    """
    Проверяет, является ли введенная команда кодом валюты.
    """
    if update.message and update.message.text:
        text = update.message.text.strip().upper()
        return text.startswith("/") and text[1:] in get_currency_codes()
    return False

def main():
    """
    Основная точка запуска Telegram-бота.
    """
    # Логируем запуск бота
    logger.info("[BOT] Запуск Telegram-бота")

    # Загружаем список валют из БД
    currency_codes = get_currency_codes()
    logger.info(f"[BOT] Загружены валютные коды: {currency_codes}")

    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("rate_on_date", rate_on_date))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("currencies_all", currencies_all))

    # Обработчик команд-кодов валют
    application.add_handler(MessageHandler(filters.Regex(r"^/[A-Z]{3,}$") & filters.TEXT, currency_today))

    # Обработчики неизвестных команд и текстовых сообщений
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(filters.TEXT, echo))

    # Запускаем бота
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("[BOT] Бот остановлен администратором.")
    except Exception as e:
        logger.error(f"[BOT] Неизвестная ошибка: {e}")

if __name__ == "__main__":
    main()
