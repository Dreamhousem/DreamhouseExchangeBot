import time
from utils.logger import logger

# Глобальная переменная для времени жизни кэша
CACHE_LIFETIME = 30 * 60  # 30 минут в секундах

# Кэш для хранения данных
# Формат: {("USD", "2024-12-12"): (значение, время добавления)}
cache = {}


def load_cache():
    """
    Загружает кэш из файла JSON.

    Returns:
        dict: Кэшированные данные.
    """
    if not os.path.exists(CACHE_FILE):
        logger.info("[CACHE] Файл кэша отсутствует, создаём новый.")
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            cache = json.load(file)
            logger.info("[CACHE] Кэш успешно загружен.")
            return cache
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

def get_from_cache(currency_code: str, date: str, cache_lifetime=CACHE_LIFETIME):
    """
    Получить значение из кэша, если оно ещё актуально.

    Args:
        currency_code (str): Код валюты (например, "USD").
        date (str): Дата в формате "YYYY-MM-DD".
        cache_lifetime (int): Время жизни кэша в секундах.

    Returns:
        float or None: Значение из кэша, если оно есть и не устарело. Иначе None.
    """
    cache = load_cache()
    key = f"{currency_code}_{date}"  # Формируем ключ для кэша
    if key in cache:
        value, timestamp = cache[key]  # Получаем значение и время добавления
        # Проверяем, не устарела ли запись
        if time.time() - timestamp <= CACHE_LIFETIME:
            logger.info(f"[CACHE] Курс {currency_code} на {date} найден в кэше: {value}")
            return value
        else:
            # Удаляем устаревшую запись            
            logger.info(f"[CACHE] Устаревшая запись для {currency_code} на {date} удалена.")
            del cache[key]
            save_cache(cache)
    return None  # Если ключ отсутствует в кэше или запись устарела


def add_to_cache(currency_code: str, date: str, rate: float):
    """
    Добавить значение в кэш.

    Args:
        currency_code (str): Код валюты (например, "USD").
        date (str): Дата в формате "YYYY-MM-DD".
        rate (float): Курс валюты.
    """
    cache = load_cache()
    key = f"{currency_code}_{date}"  # Формируем ключ для кэша
    cache[key] = (rate, time.time())  # Сохраняем значение и время добавления
    save_cache(cache)
    logger.info(f"[CACHE] Курс {currency_code} на {date} добавлен в кэш: {rate}")

def clear_old_cache():
    """
    Очищает кэш от устаревших записей.
    """
    cache = load_cache()
    current_time = time.time()
    keys_to_delete = [key for key, (_, timestamp) in cache.items() if current_time - timestamp > CACHE_LIFETIME]

    for key in keys_to_delete:
        del cache[key]
        logger.info(f"[CACHE] Устаревшая запись {key} удалена.")
    save_cache(cache)