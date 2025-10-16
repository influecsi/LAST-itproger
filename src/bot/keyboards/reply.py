from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard():
    """Основная reply клавиатура"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    latest_news_btn = KeyboardButton(text="📰 Последние новости")
    refresh_btn = KeyboardButton(text="🔄 Обновить данные")

    keyboard.add(latest_news_btn)
    keyboard.add(refresh_btn)

    return keyboard
