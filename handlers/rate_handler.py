# Для обработки команды /rate
from telegram import Update
from telegram.ext import ContextTypes
from services.nbrb_api import get_rate_on_date

# Обработчик неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

# Обработчик текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение.")
        return
    await update.message.reply_text(update.message.text)

async def rate_on_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик для получения курса валют на указанную дату.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст команды.
    """
    if len(context.args) != 2:
        await update.message.reply_text(
            "Пожалуйста, укажите код валюты и дату в формате /rate_on_date USD 2024-12-12"
        )
        return

    currency_code = context.args[0].upper()  # Код валюты
    date = context.args[1]  # Дата

    # Получаем курс на дату
    result = get_rate_on_date(currency_code, date)

    # Отправляем пользователю результат
    await update.message.reply_text(result)
