from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import logger


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help. Отправляет список доступных команд и примеры их использования.

    Args:
        update (Update): Объект обновления Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст команды.
    """
    user = update.effective_user
    message_text = update.message.text  # Оригинальное сообщение пользователя
    logger.info(f"[HELP] User {user.full_name} (ID: {user.id}) запросил список доступных команд: {message_text}")

    help_text = """
Привет! Я помогу вам следить за курсами валют. Вот список доступных команд:

1. /start - Начать работу с ботом.
    Пример: отправьте команду, чтобы активировать взаимодействие.

2. /rate - Узнать курсы популярных валют на сегодня (USD, EUR, RUB, CNY, TRY).
    Пример: /rate

3. /rate_on_date [код валюты] [дата в формате YYYY-MM-DD] - Узнать курс валюты на определённую дату.
    Пример: /rate_on_date USD 2024-12-12

4. /currencies - Показать популярные валюты.
    Пример: /currencies

5. /currencies_all - Показать полный список валют, поддерживаемых ботом.
    Пример: /currencies_all

6. /help - Получить список доступных команд.
    Пример: /help

---

Если у вас есть вопросы или предложения, напишите их в поддержку. Удачи! 😊
"""

    await update.message.reply_text(help_text)
