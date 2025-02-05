from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from services.cache import get_from_cache, add_to_cache
from services.nbrb_api import get_rate_on_date
from db import execute_query

# Предопределённый список популярных валют
# POPULAR_CURRENCIES = ["GBP", "KZT", "PLN", "UAH", "EGP", "GEL", "AED", "VND", "CNY", "RUB", "EUR", "USD"]
# Флаги для национальных валют
CURRENCY_FLAGS = {
    "KZT": "🇰🇿",    
    "EGP": "🇪🇬",
    "GEL": "🇬🇪",
    "AED": "🇦🇪",
    "VND": "🇻🇳",
    "GBP": "🇬🇧",
    "PLN": "🇵🇱",
    "UAH": "🇺🇦",
    "CNY": "🇨🇳",
    "RUB": "🇷🇺",
    "EUR": "🇪🇺",
    "USD": "🇺🇸"
}

async def currencies_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /currencies_all. Показывает список всех валют,
    отсортированный по популярности (популярные внизу списка).

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст команды.
    """
    user = update.effective_user
    logger.info(f"[CURRENCIES_ALL] User {user.full_name} (ID: {user.id}) отправил команду: /currencies_all")

    try:
        # Загружаем список всех валют из БД
        query = """
        SELECT currency_code, currency_name, scale, request_count
        FROM currency_requests
        ORDER BY request_count ASC
        """
        results = execute_query(query)

        # Проверяем, есть ли данные
        if not results:
            await update.message.reply_text("❌ В базе данных нет данных о валютах.")
            return

        # Формируем список всех валют
        sorted_currencies = [
            f"/{code} {name} (за {scale})"
            for code, name, scale, _ in results
        ]

        # Добавляем популярные валюты в конец списка
        popular_currencies = [
            f"- /{code} {name} (за {scale})"
            for code, name, scale, _ in results if code in CURRENCY_FLAGS
        ]

        response = "\n".join(sorted_currencies + popular_currencies)

        logger.info(f"[CURRENCIES_ALL] Полный список валют отправлен пользователю {user.full_name} (ID: {user.id}).")
        await update.message.reply_text(f"📜 **Полный список валют:**\n{response}")

    except Exception as e:
        logger.error(f"[CURRENCIES] Ошибка при загрузке списка валют из БД: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке списка валют. Попробуйте позже.")    


def get_currency_codes():
    """
    Загружает список доступных валют из БД (таблица currency_requests).
    """
    try:
        query = "SELECT DISTINCT currency_code FROM currency_requests"
        results = execute_query(query)
        return {row[0] for row in results}
    except Exception as e:
        logger.error(f"[CURRENCY_HANDLER] Ошибка загрузки валют из БД: {e}")
        return set()

async def currency_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команд валют (/USD, /EUR и т. д.), отправляет курс валюты за сегодняшний день.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст команды.
    """
    user = update.effective_user
    message_text = update.message.text.strip().upper()
    logger.info(f"[CURRENCY_TODAY] User {user.full_name} (ID: {user.id}) запросил курс: {message_text}")

    # Проверяем, что команда начинается с '/'
    if not message_text.startswith('/'):
        await update.message.reply_text("❌ Ошибка: команда должна начинаться с '/'. Пример: /USD")
        return

    # Убираем '/' и получаем код валюты
    currency_code = message_text[1:].strip().upper()

    # Загружаем доступные валюты из БД
    valid_currencies = get_currency_codes()
    if currency_code not in valid_currencies:
        await update.message.reply_text(f"❌ Ошибка: {currency_code} не поддерживается.")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"[CURRENCY_TODAY] Проверяем курс {currency_code} на {today}...")

    # Проверяем кэш
    rate = get_from_cache(currency_code, today)
    if rate is None:
        logger.info(f"[CURRENCY_TODAY] Курс {currency_code} отсутствует в кэше, запрашиваем API...")
        rate = get_rate_on_date(currency_code, today)
        if rate:
            add_to_cache(currency_code, today, rate)
            logger.info(f"[CURRENCY_TODAY] Курс {currency_code} получен через API и добавлен в кэш: {rate}")
        else:
            logger.warning(f"[CURRENCY_TODAY] Курс {currency_code} недоступен даже после запроса в API.")
            await update.message.reply_text(f"❌ Курс {currency_code} на {today} недоступен.")
            return

    # Получаем название валюты, масштаб и флаг
    details = execute_query(
        "SELECT currency_name, scale FROM currency_requests WHERE currency_code = ? LIMIT 1",
        (currency_code,)
    )

    currency_name = currency_code  # По умолчанию, если в БД нет данных
    scale = 1  # По умолчанию
    flag = CURRENCY_FLAGS.get(currency_code, "🏳")  # Если флага нет, ставим белый флаг 🏳

    if details:
        currency_name, scale = details[0]

    response_message = f"💰 /{currency_code} {currency_name}: {rate} BYN (за {scale} {flag}) на {today}"

    await update.message.reply_text(response_message)
    logger.info(f"[CURRENCY_TODAY] Ответ отправлен пользователю {user.full_name} (ID: {user.id}): {response_message}")