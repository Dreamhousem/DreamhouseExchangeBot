import requests
from datetime import datetime
from utils.logger import logger
from services.cache import get_from_cache, add_to_cache

# Базовый URL для запросов к API Нацбанка РБ
BASE_URL = "https://api.nbrb.by/exrates/rates/"

def get_rate_on_date(currency_code: str, date: str) -> str:
    """
    Получить курс валюты на определённую дату.

    Args:
        currency_code (str): Код валюты (например, "USD", "EUR").
        date (str): Дата в формате YYYY-MM-DD.

    Returns:
        str: Курс валюты или сообщение об ошибке.
    """
    try:
        # Проверяем корректность формата даты
        datetime.strptime(date, "%Y-%m-%d")

        # Проверяем, есть ли курс валюты в кэше
        cached_rate = get_from_cache(currency_code, date)
        if cached_rate is not None:
            # Если курс найден в кэше, логируем это и возвращаем результат
            logger.info(f"[CACHE] Курс {currency_code} на {date} найден в кэше: {cached_rate}")
            return f"Курс {currency_code} на {date}: {cached_rate} BYN"

        # Если курса нет в кэше, формируем запрос к API
        url = f"{BASE_URL}{currency_code}?parammode=2&ondate={date}"
        response = requests.get(url)

        # Обрабатываем успешный запрос
        if response.status_code == 200:
            data = response.json()
            rate = data.get("Cur_OfficialRate")  # Получаем официальный курс из ответа
            if rate:
                # Добавляем курс в кэш
                add_to_cache(currency_code, date, rate)
                # Логируем успешный запрос и возвращаем результат
                logger.info(f"[API] Успешный запрос {url}, результат: {rate}")
                return f"Курс {currency_code} на {date}: {rate} BYN"
        else:
            # Логируем ошибочный статус ответа
            logger.warning(f"[API] Ошибка запроса {url}, статус: {response.status_code}")
            return f"Ошибка: API вернул статус {response.status_code}. Проверьте данные."
    except ValueError:
        # Логируем ошибку формата даты и возвращаем сообщение об ошибке
        logger.error(f"[API] Некорректный формат даты: {date}")
        return "Ошибка: Некорректный формат даты. Используйте формат YYYY-MM-DD."
    except requests.exceptions.RequestException as e:
        # Логируем ошибку соединения с API и возвращаем сообщение об ошибке
        logger.error(f"[API] Ошибка соединения с API: {e}")
        return "Ошибка соединения с API."
