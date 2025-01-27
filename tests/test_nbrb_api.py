import unittest
from unittest.mock import patch
from services.nbrb_api import get_rate_on_date

class TestNbrbApi(unittest.TestCase):
    @patch("services.nbrb_api.requests.get")
    def test_get_rate_on_date_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"Cur_OfficialRate": 3.5}
        result = get_rate_on_date("USD", "2024-12-12")
        self.assertEqual(result, "Курс USD на 2024-12-12: 3.5 BYN")

    @patch("services.nbrb_api.requests.get")
    def test_get_rate_on_date_fail(self, mock_get):
        mock_get.return_value.status_code = 404
        result = get_rate_on_date("USD", "2024-12-12")
        self.assertIn("Ошибка: API вернул статус 404", result)


    # def test_get_rate_on_date_connection_error(self):
    #     # Тест с ошибкой соединения с API
    #     with patch("services.nbrb_api.requests.get") as mock_get:
    #         mock_get.side_effect = requests.exceptions.RequestException("Connection error")
    #         result = get_rate_on_date("USD", "2024-12-12")
    #         self.assertIn("Ошибка соединения с API", result)

    # def test_get_rate_on_date_invalid_currency(self):
    #     # Тест с некорректным кодом валюты
    #     result = get_rate_on_date("INVALID", "2024-12-12")
    #     self.assertIn("Ошибка: Некорректный код валюты", result)

    # def test_get_rate_on_date_empty_currency(self):
    #     # Тест с пустым кодом валюты
    #     result = get_rate_on_date("", "2024-12-12")
    #     self.assertIn("Ошибка: Некорректный код валюты", result)

    