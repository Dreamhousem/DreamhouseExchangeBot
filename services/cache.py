import os
import json
import time
from utils.logger import logger

# Файл для хранения кэша
CACHE_FILE = "data/cache.json"

# Время жизни кэша в секундах (30 минут)
CACHE_LIFETIME = 30 * 60  

def ensure_cache_file():
    """
    Убедиться, что файл кэша существует. Если его нет, создать пустой JSON.
    """
    if not os.path.exists("data"):
        os.makedirs("data")  # Создаём папку data, если её нет
        logger.info("[CACHE] Папка 'data' была создана.")

    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file)  # Создаём пустой JSON
        logger.info("[CACHE] Файл кэша 'cache.json' был создан.")

def load_cache():
    """
    Загружает кэш из файла JSON.
    
    Returns:
        dict: Кэшированные данные.
    """
    ensure_cache_file()  # Убеждаемся, что файл существует

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            cache = json.load(file)
            logger.info("[CACHE] Кэш успешно загружен.")
            return cache
    except json.JSONDecodeError:
        logger.error("[CACHE] Ошибка чтения JSON, файл повреждён. Очищаем кэш.")
        save_cache({})  # Очищаем повреждённый кэш
        return {}
    except Exception as e:
        logger.error(f"[CACHE] Ошибка загрузки кэша: {e}")
        return {}

def save_cache(cache):
    """
    Сохраняет кэш в файл JSON.

    Args:
        cache (dict): Данные для сохранения.
    """
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump(cache, file, ensure_ascii=False, indent=4)
        logger.info("[CACHE] Кэш успешно сохранён.")
    except Exception as e:
        logger.error(f"[CACHE] Ошибка сохранения кэша: {e}")

def get_from_cache(currency_code: str, date: str):
    """
    Получить значение из кэша, если оно ещё актуально.

    Args:
        currency_code (str): Код валюты (например, "USD").
        date (str): Дата в формате "YYYY-MM-DD".

    Returns:
        float or None: Значение из кэша, если оно есть и не устарело. Иначе None.
    """
    cache = load_cache()
    key = f"{currency_code}_{date}"

    if key in cache:
        value, timestamp = cache[key]
        if time.time() - timestamp <= CACHE_LIFETIME:
            logger.info(f"[CACHE] Курс {currency_code} на {date} найден в кэше: {value}")
            return value
        else:
            del cache[key]  # Удаляем устаревшую запись
            save_cache(cache)
            logger.info(f"[CACHE] Устаревшая запись для {currency_code} на {date} удалена.")

    return None  # Курс не найден в кэше или устарел

def add_to_cache(currency_code: str, date: str, rate: float):
    """
    Добавить значение в кэш.

    Args:
        currency_code (str): Код валюты (например, "USD").
        date (str): Дата в формате "YYYY-MM-DD".
        rate (float): Курс валюты.
    """
    # save_cache({})  # Очищаем кэш перед добавлением нового значения
    cache = load_cache()
    key = f"{currency_code}_{date}"

    # Избавляемся от лишнего текста, храним только число
    if isinstance(rate, str) and "BYN" in rate:
        rate = float(rate.split(":")[-1].strip().split(" ")[0])

    cache[key] = (rate, time.time())  # Сохраняем только курс и время записи
    save_cache(cache)
    logger.info(f"[CACHE] Курс {currency_code} на {date} добавлен в кэш: {rate}")

def clear_old_cache():
    """
    Очищает устаревшие записи из кэша.
    """
    cache = load_cache()
    current_time = time.time()

    keys_to_delete = [key for key, (_, timestamp) in cache.items() if current_time - timestamp > CACHE_LIFETIME]

    for key in keys_to_delete:
        del cache[key]
        logger.info(f"[CACHE] Устаревшая запись {key} удалена.")

    save_cache(cache)
