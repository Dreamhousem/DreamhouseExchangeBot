import json
import os
import requests
from datetime import datetime
from utils.logger import logger

CURRENCY_REFERENCE_FILE = os.path.join("data", "currencies.json")  # Путь к файлу справочника
API_URL = "https://api.nbrb.by/exrates/currencies"

def ensure_data_directory():
    """
    Убедиться, что папка `data` существует. Если нет, создаёт её.
    """
    if not os.path.exists("data"):
        os.makedirs("data")
        logger.info("[CURRENCY_REFERENCE] Папка 'data' создана.")


def create_currency_reference():
    """
    Создаёт справочник валют на основе данных из API Нацбанка.
    """
    try:
        logger.info("[CURRENCY_REFERENCE] Начинаем создание справочника валют...")
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        currencies = {}
        for item in data:
            currencies[item["Cur_Abbreviation"]] = {
                "name": item["Cur_Name"],
                "scale": item["Cur_Scale"]
            }

        # Сохраняем справочник в файл
        ensure_data_directory()
        with open(CURRENCY_REFERENCE_FILE, "w", encoding="utf-8") as file:
            json.dump(currencies, file, ensure_ascii=False, indent=4)
        logger.info("[CURRENCY_REFERENCE] Справочник валют успешно создан.")
    except requests.exceptions.RequestException as e:
        logger.error(f"[CURRENCY_REFERENCE] Ошибка при запросе к API: {e}")
    except Exception as e:
        logger.error(f"[CURRENCY_REFERENCE] Неизвестная ошибка: {e}")


def load_currency_reference():
    """
    Загружает справочник валют из локального файла.
    """
    if not os.path.exists(CURRENCY_REFERENCE_FILE):
        logger.warning("[CURRENCY_REFERENCE] Справочник валют отсутствует. Создаём новый.")
        create_currency_reference()

    with open(CURRENCY_REFERENCE_FILE, "r", encoding="utf-8") as file:
        logger.info("[CURRENCY_REFERENCE] Справочник валют успешно загружен.")
        return json.load(file)


def update_currency_reference():
    """
    Обновляет справочник валют, если он устарел.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(CURRENCY_REFERENCE_FILE):
        last_modified = datetime.fromtimestamp(os.path.getmtime(CURRENCY_REFERENCE_FILE)).strftime("%Y-%m-%d")
    else:
        last_modified = None

    if last_modified != today:
        logger.info("[CURRENCY_REFERENCE] Обновление справочника валют...")
        create_currency_reference()
    else:
        logger.info("[CURRENCY_REFERENCE] Справочник актуален.")
