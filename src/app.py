import logging
from loader import bot
import bot.handlers.user_handlers
import bot.handlers.callback_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Упрощенная версия запуска"""
    print("🤖 Запуск бота для парсинга ITproger...")

    try:
        # Простой запуск без лишних методов
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=20,
            logger_level=logging.INFO
        )
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print("🛑 Бот остановлен")


if __name__ == "__main__":
    main()
