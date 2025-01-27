import unittest
from unittest.mock import AsyncMock, MagicMock
from handlers.start_handler import start
from handlers.help_handler import help_command

class TestHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_start_handler(self):
        # Создаём моки для update и context
        update = MagicMock()
        context = MagicMock()

        # Мокаем данные пользователя
        update.message.from_user.first_name = "Test User"
        update.message.reply_text = AsyncMock()

        # Вызываем обработчик
        await start(update, context)

        # Проверяем вызов функции reply_text
        update.message.reply_text.assert_called_once_with(
            "Привет, Test User! Я помогу вам следить за курсами валют Национального банка РБ. "
            "Используйте команду /help, чтобы узнать больше о возможностях бота."
        )

    async def test_help_handler(self):
        # Создаём моки для update и context
        update = MagicMock()
        context = MagicMock()

        update.message.reply_text = AsyncMock()

        # Вызываем обработчик
        await help_command(update, context)

        # Проверяем вызов функции reply_text
        update.message.reply_text.assert_called_once()

    async def test_currencies_all_handler(self):
        update = MagicMock()
        context = MagicMock()
        # Загружаем mock-данные для справочника
        load_currency_reference.return_value = {
            "USD": {"name": "Доллар США", "scale": 1},
            "EUR": {"name": "Евро", "scale": 1},
            "RUB": {"name": "Российский рубль", "scale": 100},
            "CNY": {"name": "Китайский юань", "scale": 10},
        }
        # Вызываем команду /currencies_all
        await currencies_all(update, context)
        # проверяем, что вызов вызов был выполнен с ожидаемым ответом
        update.message.reply_text.assert_called_once(
            "Полный список валют:\n"
            "- USD: Доллар США (за 1)\n"
            "- EUR: Евро (за 1)\n"
            "- RUB: Российский рубль (за 100)\n"
            "- CNY: Китайский юань (за 10)"
        )