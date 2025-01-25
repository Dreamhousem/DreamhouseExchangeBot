# venv\Scripts\activate
# python bot.py

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config.config import TOKEN
from handlers.start_handler import start
from handlers.rate_handler import rate_on_date, echo, unknown

def main():
    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate_on_date", rate_on_date))  # Новый обработчик
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(filters.TEXT, echo))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
