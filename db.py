import sqlite3
import os
from datetime import datetime
from utils.logger import logger
from services.nbrb_api import get_rate_on_date  # Импорт API для запроса курса валют

DB_PATH = "data/bot_database.db"  # Путь к файлу базы данных


def ensure_database():
    """
    Убедиться, что база данных и её папка существуют.
    """
    if not os.path.exists("data"):
        os.makedirs("data")
        logger.info("[DB] Папка 'data' была создана.")

    if not os.path.exists(DB_PATH):
        open(DB_PATH, "w").close()
        logger.info("[DB] Файл базы данных был создан.")

def execute_query(query, params=None):
    """
    Выполняет SQL-запрос и возвращает результат.

    Args:
        query (str): SQL-запрос.
        params (tuple, optional): Параметры для запроса. Defaults to None.

    Returns:
        list: Результаты запроса.
    """
    ensure_database()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            logger.info(f"[DB] Успешно выполнен запрос: {query} с параметрами {params}")
            return result
        except sqlite3.Error as e:
            logger.error(f"[DB] Ошибка выполнения запроса: {e}")
            return []

def create_tables():
    """
    Создаёт все необходимые таблицы в базе данных.
    """
    ensure_database()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            subscribed_at DATETIME NOT NULL,
            status BOOLEAN NOT NULL DEFAULT 1
        )
        """)

        # Таблица курсов валют
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_code TEXT NOT NULL,
            currency_name TEXT NOT NULL,
            scale INTEGER NOT NULL,
            date DATE NOT NULL,
            rate REAL NOT NULL
        )
        """)

        # Таблица запросов валют
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS currency_requests (
            currency_code TEXT PRIMARY KEY,
            request_count INTEGER DEFAULT 0
        )
        """)

        conn.commit()
        logger.info("[DB] Все таблицы успешно созданы.")

def add_user(telegram_id, full_name):
    """
    Добавляет пользователя в базу данных.

    Args:
        telegram_id (int): Уникальный Telegram ID.
        full_name (str): Полное имя пользователя.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO users (telegram_id, full_name, subscribed_at, status)
            VALUES (?, ?, ?, 1)
            """, (telegram_id, full_name, datetime.now()))
            conn.commit()
            logger.info(f"[DB] Пользователь {full_name} (ID: {telegram_id}) добавлен.")
        except sqlite3.IntegrityError:
            logger.warning(f"[DB] Пользователь {full_name} (ID: {telegram_id}) уже существует.")


def add_user_preference(user_id, currency_code):
    """
    Добавляет предпочтение валюты для пользователя.

    Args:
        user_id (int): ID пользователя в базе данных.
        currency_code (str): Код валюты.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO user_preferences (user_id, currency_code)
        VALUES (?, ?)
        """, (user_id, currency_code))
        conn.commit()
        logger.info(f"[DB] Добавлено предпочтение валюты {currency_code} для пользователя {user_id}.")


def increment_currency_request(currency_code):
    """
    Увеличивает счётчик запросов для указанной валюты.

    Args:
        currency_code (str): Код валюты.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO currency_requests (currency_code, request_count)
        VALUES (?, 1)
        ON CONFLICT(currency_code)
        DO UPDATE SET request_count = request_count + 1
        """, (currency_code,))
        conn.commit()
        logger.info(f"[DB] Счётчик запросов для валюты {currency_code} увеличен.")

def update_exchange_rates(POPULAR_CURRENCIES):
    """
    Обновляет курсы популярных валют в БД за текущую дату.

    Args:
        POPULAR_CURRENCIES (list): Список популярных валют.
    """
    from services.nbrb_api import get_rate_on_date
    today = datetime.now().strftime("%Y-%m-%d")

    logger.info("[DB] Начинаем обновление курсов валют в БД...")

    for currency in POPULAR_CURRENCIES:
        logger.info(f"[DB] Запрашиваем курс для {currency} на {today}...")

        rate = get_rate_on_date(currency, today)

        if rate:
            query = """
            INSERT OR REPLACE INTO exchange_rates (currency_code, currency_name, scale, date, rate)
            VALUES (?, ?, ?, ?, ?)
            """
            details = execute_query(
                "SELECT currency_name, scale FROM currency_requests WHERE currency_code = ?",
                (currency,)
            )

            if details:
                currency_name, scale = details[0]
                execute_query(query, (currency, currency_name, scale, today, rate))
                logger.info(f"[DB] Курс {currency} ({rate} BYN) на {today} успешно обновлён в БД.")
            else:
                logger.warning(f"[DB] Нет данных о {currency} в currency_requests, пропускаем обновление.")
        else:
            logger.warning(f"[DB] Не удалось получить курс {currency} на {today} через API.")

    logger.info("[DB] Обновление курсов валют завершено.")