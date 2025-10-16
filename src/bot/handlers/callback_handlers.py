from loader import bot
from bot.parser.itproger_parser import ItProgerParser
from bot.keyboards.inline import get_news_keyboard

parser = ItProgerParser()

@bot.callback_query_handler(func=lambda call: call.data == "refresh_news")
def refresh_news_callback(call):
    """Обновление новостей по инлайн кнопке"""
    bot.answer_callback_query(call.id, "🔄 Обновляем новости...")
    
    news = parser.get_news(count=5)
    
    if not news:
        bot.edit_message_text(
            "❌ Не удалось обновить новости. Попробуйте позже.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    # Обновляем сообщение
    news_text = "<b>📰 Обновленные новости ITproger:</b>\n\n"
    
    for i, item in enumerate(news, 1):
        news_text += f"<b>{i}. {item['title']}</b>\n"
        if item['description']:
            news_text += f"{item['description']}\n"
        if item['date']:
            news_text += f"<i>📅 {item['date']}</i>\n"
        news_text += "\n"
    
    bot.edit_message_text(
        news_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=get_news_keyboard(news),
        parse_mode='HTML'
    )