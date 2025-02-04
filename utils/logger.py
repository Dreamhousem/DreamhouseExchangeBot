import logging
from logging.handlers import RotatingFileHandler
import os

# Создаём папку для логов
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Путь к файлу логов
LOG_FILE = os.path.join(LOG_DIR, "bot_logs.log")

def setup_logger():
    """
    Настраивает логирование для проекта Telegram Bot.

    Returns:
        logging.Logger: Логгер с уникальным именем "TelegramBotLogger".
    """
    logger = logging.getLogger("TelegramBotLogger")  # Уникальное имя логгера

    # Устанавливаем уровень логирования только если обработчики ещё не добавлены
    if not logger.handlers:
        logger.setLevel(logging.INFO)  # Уровень логирования: INFO

        # Создаём обработчик для ротации логов
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # Ограничение размера файла логов: 5 MB
            backupCount=3,  # Количество резервных файлов логов
            encoding="utf-8"  # Кодировка
        )

        # Форматирование логов
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"  # Убрали [TelegramBotLogger]
        )
        handler.setFormatter(formatter)

        # Добавляем обработчик в логгер
        logger.addHandler(handler)

        # Убедимся, что дублирование логов отключено
        logger.propagate = False

    return logger


# Глобальный логгер, доступный во всём проекте
logger = setup_logger()