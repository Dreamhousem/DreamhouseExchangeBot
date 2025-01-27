from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config.config import TOKEN
from handlers.start_handler import start
from handlers.help_handler import help_command
from utils.logger import logger
from handlers.currency_handler import currencies_all
from handlers.rate_handler import rate, rate_on_date, echo, unknown


def main():
    """
    Основная точка запуска Telegram-бота.
    """
    # Логируем запуск бота
    logger.info("[BOT] Запуск Telegram-бота")

    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("rate_on_date", rate_on_date))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("currencies_all", currencies_all))
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
