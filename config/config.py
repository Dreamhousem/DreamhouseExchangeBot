import os
from dotenv import load_dotenv
import logging

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден. Убедитесь, что файл .env содержит BOT_TOKEN.")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
