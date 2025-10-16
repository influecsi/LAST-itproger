from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot.parser.itproger_parser import ITProgerParser
from bot.keyboards.inline import get_article_keyboard
from bot.handlers.user_handlers import user_articles, user_current_index, show_article, show_fast_article
import logging

logger = logging.getLogger(__name__)

async def handle_next_article(callback: types.CallbackQuery):
    """Обработчик переключения между статьями"""
    user_id = callback.from_user.id
    data = callback.data.split(":")[1]
    
    try:
        article_index = int(data)
        await callback.message.delete()
        await show_article(callback.message, user_id, article_index)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка при переключении статьи: {e}")
        await callback.answer("❌ Ошибка при переключении статьи")
    
    await callback.answer()

async def handle_full_content(callback: types.CallbackQuery):
    """Обработчик показа полного текста статьи"""
    user_id = callback.from_user.id
    article_url = callback.data.split(":")[1]
    
    await callback.answer("🔄 Загружаю полный текст...")
    
    # Получаем полный контент асинхронно
    async with ITProgerParser() as parser:
        content_data = await parser.get_article_content(article_url)
    
    if content_data and content_data["content"]:
        # Ограничиваем длину сообщения (Telegram limit ~4096 символов)
        content = content_data["content"]
        if len(content) > 4000:
            content = content[:4000] + "\n\n... (текст обрезан)"
        
        await callback.message.answer(
            f"<b>📖 Полный текст статьи:</b>\n\n{content}",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("❌ Не удалось загрузить полный текст статьи")

async def handle_page_change(callback: types.CallbackQuery):
    """Обработчик смены страницы"""
    page = int(callback.data.split(":")[1])
    
    await callback.answer(f"🔄 Загружаю страницу {page}...")
    # Здесь можно реализовать загрузку разных страниц

def register_callback_handlers(dp: Dispatcher):
    """Регистрация всех callback обработчиков"""
    dp.register_callback_query_handler(handle_next_article, lambda c: c.data.startswith("next_article:"))
    dp.register_callback_query_handler(handle_full_content, lambda c: c.data.startswith("full_content:"))
    dp.register_callback_query_handler(handle_page_change, lambda c: c.data.startswith("page:"))