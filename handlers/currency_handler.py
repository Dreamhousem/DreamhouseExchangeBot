from telegram import Update
from telegram.ext import ContextTypes
from services.currency_reference import load_currency_reference
from utils.logger import logger
from db import execute_query  

# Предопределённый список популярных валют
POPULAR_CURRENCIES = ["USD", "EUR", "RUB", "CNY", "PLN", "UAH", "EGP", "GEL", "AED", "VND", "KZT", "GBP"]

async def currencies_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /currencies_all. Показывает список всех валют,
    отсортированный по популярности (популярные внизу списка).

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст команды.
    """
    user = update.effective_user
    message_text = update.message.text  # Оригинальное сообщение пользователя
    logger.info(f"[CURRENCIES_ALL] User {user.full_name} (ID: {user.id}) отправил команду: {message_text}")

    
    try:
        # Загружаем справочник валют
        currency_reference = load_currency_reference()
        
        # Получаем список всех валют с их счётчиками запросов
        query = """
        SELECT currency_code, request_count
        FROM currency_requests
        ORDER BY request_count ASC
        """
        results = execute_query(query)

        # Формируем список валют с учётом популярности
        sorted_currencies = [
            f"- /{code} {currency_reference[code]['name']} (за {currency_reference[code]['scale']})"
            for code, _ in results if code in currency_reference
        ]

        # Добавляем популярные валюты в конец списка
        popular_currencies = [
            f"- /{code} {currency_reference[code]['name']} (за {currency_reference[code]['scale']})"
            for code in POPULAR_CURRENCIES if code in currency_reference
        ]

        response = "\n".join(sorted_currencies + popular_currencies)

        logger.info(f"[CURRENCIES_ALL] Полный список валют отправлен пользователю {user.full_name} (ID: {user.id}).")
        await update.message.reply_text(f"Полный список валют:\n{response}")

    except Exception as e:
        logger.error(f"[CURRENCIES] Ошибка при загрузке справочника валют: {e}")
        await update.message.reply_text("Произошла ошибка при загрузке справочника валют. Пожалуйста, попробуйте позже.")
        return
    
    
