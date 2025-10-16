from telebot import types
from loader import bot

def get_news_keyboard(news_items):
    """Создает инлайн клавиатуру с новостями"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for i, news in enumerate(news_items[:5], 1):
        if news.get('link'):
            btn = types.InlineKeyboardButton(
                text=f"📰 {i}. {news['title'][:30]}...",
                url=news['link']
            )
            keyboard.add(btn)
    
    # Кнопка обновления
    refresh_btn = types.InlineKeyboardButton(
        text="🔄 Обновить новости", 
        callback_data="refresh_news"
    )
    keyboard.add(refresh_btn)
    
    return keyboard

def get_main_keyboard():
    """Основная клавиатура"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        types.KeyboardButton("📰 Последние новости"),
        types.KeyboardButton("🔄 Обновить"),
        types.KeyboardButton("❓ Помощь")
    ]
    
    keyboard.add(*buttons)
    return keyboard