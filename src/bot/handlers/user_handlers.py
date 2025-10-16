from loader import bot
from bot.parser.itproger_parser import ItProgerParser
from bot.keyboards.inline import get_news_keyboard, get_main_keyboard
import logging

logger = logging.getLogger(__name__)
parser = ItProgerParser()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    welcome_text = """
🤖 <b>Бот для парсинга новостей ITproger</b>

Доступные команды:
📰 /news - Последние новости
🔄 /refresh - Обновить новости
❓ /help - Помощь

Или используйте кнопки ниже!
    """
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

@bot.message_handler(commands=['news'])
@bot.message_handler(func=lambda message: message.text == "📰 Последние новости")
def send_news(message):
    """Отправка последних новостей"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    news = parser.get_news(count=5)
    
    if not news:
        bot.send_message(
            message.chat.id,
            "❌ Не удалось получить новости. Попробуйте позже."
        )
        return
    
    # Формируем сообщение
    news_text = "<b>📰 Последние новости ITproger:</b>\n\n"
    
    for i, item in enumerate(news, 1):
        news_text += f"<b>{i}. {item['title']}</b>\n"
        if item['description']:
            news_text += f"{item['description']}\n"
        if item['date']:
            news_text += f"<i>📅 {item['date']}</i>\n"
        news_text += "\n"
    
    # Отправляем сообщение с клавиатурой
    bot.send_message(
        message.chat.id,
        news_text,
        reply_markup=get_news_keyboard(news),
        parse_mode='HTML'
    )

@bot.message_handler(commands=['refresh'])
@bot.message_handler(func=lambda message: message.text == "🔄 Обновить")
def refresh_news(message):
    """Обновление новостей"""
    bot.send_message(
        message.chat.id,
        "🔄 Обновляю новости...",
        reply_markup=get_main_keyboard()
    )
    send_news(message)

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "❓ Помощь")
def send_help(message):
    """Помощь по боту"""
    help_text = """
<b>📖 Помощь по боту:</b>

🤖 <b>Бот для парсинга новостей с ITproger.com</b>

<b>Команды:</b>
/start - Запуск бота
/news - Последние новости  
/refresh - Обновить новости
/help - Эта справка

<b>Как использовать:</b>
1. Нажмите "📰 Последние новости"
2. Выберите интересующую новость из списка
3. Используйте "🔄 Обновить" для получения свежих новостей

<b>Примечание:</b> Парсер может требовать обновления при изменении структуры сайта.
    """
    
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработчик любых других сообщений"""
    bot.reply_to(
        message,
        "🤖 Используйте кнопки ниже или команды:\n/start, /news, /help",
        reply_markup=get_main_keyboard()
    )