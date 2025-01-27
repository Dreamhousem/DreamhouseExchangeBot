import unittest
import time
from services.cache import get_from_cache, add_to_cache

class TestCache(unittest.TestCase):
    """
    Набор тестов для проверки работы функций кэширования.
    """

    def setUp(self):
        """
        Метод, который вызывается перед каждым тестом.
        Используется для подготовки окружения: очистки кэша.
        """
        global cache  # Доступ к глобальному кэшу
        cache = {}  # Очищаем кэш перед каждым тестом

    def test_add_to_cache(self):
        """
        Тест: Проверяем, что значение корректно добавляется в кэш и извлекается.
        """
        add_to_cache("USD", "2024-12-12", 3.5)  # Добавляем данные в кэш
        # Проверяем, что данные извлекаются корректно
        self.assertEqual(get_from_cache("USD", "2024-12-12"), 3.5)

    def test_expired_cache(self):
        """
        Тест: Проверяем, что устаревшие данные удаляются из кэша.
        """
        add_to_cache("USD", "2024-12-12", 3.5)  # Добавляем данные в кэш
        time.sleep(1)  # Ждём, чтобы эмулировать истечение времени жизни записи
        # Передаём кастомное время жизни (1 секунда), чтобы запись устарела
        self.assertIsNone(get_from_cache("USD", "2024-12-12", cache_lifetime=1))


    def test_