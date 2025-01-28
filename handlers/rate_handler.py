from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger
from services.cache import get_from_cache, add_to_cache
from db import execute_query, update_exchange_rates
from services.nbrb_api import get_rate_on_date
import time

# Список популярных валют
POPULAR_CURRENCIES = ["USD", "EUR", "RUB", "CNY"]

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /rate. Отправляет текущие курсы популярных валют.
    """
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"[RATE] User {user.full_name} (ID: {user.id}) запросил курсы валют: {message_text}")

    today = datetime.now().strftime("%Y-%m-%d")
    responses = []

    for currency in POPULAR_CURRENCIES:
        logger.info(f"[RATE] Проверяем курс {currency} на {today}...")

        try:
            # Проверяем кэш
            rate = get_from_cache(currency, today)
            if rate is not None:
                logger.info(f"[RATE] Курс {currency} найден в кэше: {rate}")
            else:
                logger.info(f"[RATE] Курс {currency} отсутствует в кэше, проверяем БД...")
                query = "SELECT rate FROM exchange_rates WHERE currency_code = ? AND date = ? LIMIT 1"
                result = execute_query(query, (currency, today))

                if result:
                    rate = result[0][0]
                    add_to_cache(currency, today, rate)
                    logger.info(f"[RATE] Курс {currency} найден в БД: {rate}")
                else:
                    logger.info(f"[RATE] Курс {currency} отсутствует в БД, обновляем данные через API...")
                    update_exchange_rates(POPULAR_CURRENCIES)
                    rate = get_from_cache(currency, today)

            if rate:
                details = execute_query(
                    "SELECT currency_name, scale FROM currency_requests WHERE currency_code = ? LIMIT 1",
                    (currency,)
                )
                if details:
                    currency_name, scale = details[0]
                    responses.append(f"/{currency} {currency_name}: **{rate} BYN** (за {scale})")
                    logger.info(f"[RATE] Добавлено в ответ: {currency_name} ({rate} BYN за {scale})")
                else:
                    responses.append(f"/{currency}: Курс найден, но информация отсутствует.")
                    logger.warning(f"[RATE] Нет данных о {currency} в таблице currency_requests.")
            else:
                responses.append(f"/{currency}: Курс недоступен.")
                logger.warning(f"[RATE] Курс {currency} недоступен.")

        except Exception as e:
            logger.error(f"[RATE] Ошибка при обработке {currency}: {e}")

    if responses:
        message_text = f"💰 **Курсы валют на {today}:**\n" + "\n".join(responses)
    else:
        message_text = "❌ Не удалось получить курсы валют. Попробуйте позже."
        logger.error("[RATE] Итоговый ответ пуст, возможно, произошла ошибка.")

    await update.message.reply_text(message_text)
    logger.info(f"[RATE] Ответ пользователю {user.full_name} (ID: {user.id}): {message_text}")


async def rate_on_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /rate_on_date. Отправляет курс указанной валюты на выбранную дату.
    """
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"[RATE_ON_DATE] User {user.full_name} (ID: {user.id}) запросил: {message_text}")

    if len(context.args) != 2:
        error_message = "❌ Пожалуйста, укажите код валюты и дату в формате: /rate_on_date USD 2024-12-12"
        await update.message.reply_text(error_message)
        logger.warning(f"[RATE_ON_DATE] Некорректный запрос от {user.full_name} (ID: {user.id}): {message_text}")
        return

    currency_code = context.args[0].upper()
    date = context.args[1]

    logger.info(f"[RATE_ON_DATE] Проверяем курс {currency_code} на {date}...")

    rate = get_from_cache(currency_code, date)
    if rate is not None:
        logger.info(f"[RATE_ON_DATE] Курс {currency_code} найден в кэше: {rate}")
    else:
        logger.info(f"[RATE_ON_DATE] Курс {currency_code} отсутствует в кэше, проверяем БД...")

        query = "SELECT rate FROM exchange_rates WHERE currency_code = ? AND date = ? LIMIT 1"
        result = execute_query(query, (currency_code, date))

        if result:
            rate = result[0][0]
            add_to_cache(currency_code, date, rate)
            logger.info(f"[RATE_ON_DATE] Курс {currency_code} найден в БД: {rate}")
        else:
            logger.info(f"[RATE_ON_DATE] Курс {currency_code} отсутствует в БД, запрашиваем через API...")
            rate = get_rate_on_date(currency_code, date)
            
            if rate:
                add_to_cache(currency_code, date, rate)
                logger.info(f"[RATE_ON_DATE] Курс {currency_code} получен через API и добавлен в кэш: {rate}")
            else:
                logger.warning(f"[RATE_ON_DATE] Курс {currency_code} недоступен даже после запроса в API.")

    if rate:
        query = "SELECT currency_name, scale FROM currency_requests WHERE currency_code = ? LIMIT 1"
        details = execute_query(query, (currency_code,))

        if details:
            currency_name, scale = details[0]
            response_message = f"💰 /{currency_code} {currency_name}: **{rate} BYN** (за {scale}) на {date}"
            await update.message.reply_text(response_message)
            logger.info(f"[RATE_ON_DATE] Ответ отправлен пользователю {user.full_name} (ID: {user.id}): {response_message}")
        else:
            error_message = f"❌ Информация о {currency_code} отсутствует в базе данных."
            await update.message.reply_text(error_message)
            logger.warning(f"[RATE_ON_DATE] {error_message}")
    else:
        error_message = f"❌ Курс {currency_code} на {date} недоступен."
        await update.message.reply_text(error_message)
        logger.warning(f"[RATE_ON_DATE] {error_message}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик текстовых сообщений. Повторяет сообщение пользователя.
    """
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"[ECHO] User {user.full_name} (ID: {user.id}) отправил сообщение: {message_text}")
    await update.message.reply_text(message_text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик неизвестных команд. Сообщает пользователю, что команда неизвестна.
    """
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"[UNKNOWN] User {user.full_name} (ID: {user.id}) отправил неизвестную команду: {message_text}")
    await update.message.reply_text(
        "❌ Извините, я не понимаю эту команду. Попробуйте использовать /help для получения списка доступных команд."
    )
