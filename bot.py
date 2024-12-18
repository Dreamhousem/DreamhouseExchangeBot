import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Я помогу вам следить за курсами валют.")

def main():
    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
