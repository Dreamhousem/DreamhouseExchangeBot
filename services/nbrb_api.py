import requests
import logging
from datetime import datetime

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
        # Проверяем формат даты
        datetime.strptime(date, "%Y-%m-%d")
        # Формируем URL с параметрами
        url = f"{BASE_URL}{currency_code}?parammode=2&ondate={date}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            rate = data.get("Cur_OfficialRate")
            return f"Курс {currency_code} на {date}: {rate} BYN"
        else:
            return f"Ошибка: API вернул статус {response.status_code}. Проверьте данные."
    except ValueError:
        return "Ошибка: Некорректный формат даты. Используйте формат YYYY-MM-DD."
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к API: {e}")
        return "Ошибка соединения с API."
