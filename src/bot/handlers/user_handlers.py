from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot.parser.itproger_parser import ITProgerParser
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_article_keyboard
import logging
import asyncio

# Глобальные переменные для хранения состояния
user_articles = {}
user_current_index = {}

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    
    welcome_text = (
        "🤖 Добро пожаловать в IT News Bot!\n\n"
        "Я помогу вам быть в курсе последних IT новостей с itproger.com\n\n"
        "📝 <b>Доступные команды:</b>\n"
        "• /start - начать работу\n"
        "• /news - показать последние новости\n"
        "• /fast_news - быстрые новости (без картинок)\n"
        "• 🔄 Обновить данные - обновить список новостей\n"
        "• 📰 Последние новости - показать свежие статьи\n\n"
        "⚡ <b>Совет:</b> Используйте /fast_news для более быстрой загрузки!"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode='HTML')
    logger.info("Ответ на /start отправлен")

async def cmd_fast_news(message: types.Message):
    """Быстрые новости без картинок"""
    user_id = message.from_user.id
    logger.info(f"Запрос быстрых новостей от пользователя {user_id}")
    
    progress_msg = await message.answer("⚡ Загружаю новости...")
    
    async with ITProgerParser() as parser:
        articles = await parser.get_news_list(page=1)
    
    if not articles:
        await progress_msg.edit_text("❌ Не удалось загрузить новости. Попробуйте позже.")
        return
    
    # Сохраняем статьи для пользователя
    user_articles[user_id] = articles
    user_current_index[user_id] = 0
    
    # Удаляем сообщение о загрузке
    await progress_msg.delete()
    
    # Показываем первую статью без изображения
    await show_fast_article(message, user_id, 0)

async def show_fast_article(message: types.Message, user_id: int, article_index: int):
    """Показать статью в быстром режиме (без изображения)"""
    articles = user_articles.get(user_id)
    
    if not articles or article_index >= len(articles):
        await message.answer("❌ Статьи не найдены. Запросите новости снова.")
        return
    
    article = articles[article_index]
    
    # Формируем сообщение
    text = (
        f"📰 <b>{article['title']}</b>\n\n"
        f"{article['description']}\n\n"
        f"📎 <a href='{article['url']}'>Читать на сайте</a>\n\n"
        f"<i>Статья {article_index + 1} из {len(articles)}</i>"
    )
    
    await message.answer(
        text,
        reply_markup=get_article_keyboard(
            article['url'], 
            article_index, 
            len(articles)
        ),
        parse_mode='HTML',
        disable_web_page_preview=True
    )

async def show_latest_news(message: types.Message):
    """Показать последние новости с изображениями"""
    user_id = message.from_user.id
    logger.info(f"Запрос новостей от пользователя {user_id}")
    
    progress_msg = await message.answer("🔄 Загружаю последние новости...")
    
    async with ITProgerParser() as parser:
        articles = await parser.get_news_list(page=1)
    
    if not articles:
        await progress_msg.edit_text("❌ Не удалось загрузить новости. Попробуйте позже.")
        return
    
    # Сохраняем статьи для пользователя
    user_articles[user_id] = articles
    user_current_index[user_id] = 0
    
    # Удаляем сообщение о загрузке
    await progress_msg.delete()
    
    # Показываем первую статью
    await show_article(message, user_id, 0)

async def show_article(message: types.Message, user_id: int, article_index: int):
    """Показать конкретную статью с изображением"""
    articles = user_articles.get(user_id)
    
    if not articles or article_index >= len(articles):
        await message.answer("❌ Статьи не найдены. Запросите новости снова.")
        return
    
    article = articles[article_index]
    
    # Формируем сообщение
    caption = (
        f"<b>{article['title']}</b>\n\n"
        f"{article['description']}\n\n"
        f"<i>Статья {article_index + 1} из {len(articles)}</i>"
    )
    
    # Отправляем изображение если есть
    if article['image']:
        try:
            await message.answer_photo(
                photo=article['image'],
                caption=caption,
                reply_markup=get_article_keyboard(
                    article['url'], 
                    article_index, 
                    len(articles)
                ),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке фото: {e}")
            # Если не удалось отправить фото, отправляем текстом
            await message.answer(
                caption,
                reply_markup=get_article_keyboard(
                    article['url'], 
                    article_index, 
                    len(articles)
                ),
                parse_mode='HTML'
            )
    else:
        await message.answer(
            caption,
            reply_markup=get_article_keyboard(
                article['url'], 
                article_index, 
                len(articles)
            ),
            parse_mode='HTML'
        )

async def refresh_news(message: types.Message):
    """Обновить данные"""
    user_id = message.from_user.id
    
    # Очищаем кеш пользователя
    if user_id in user_articles:
        del user_articles[user_id]
    if user_id in user_current_index:
        del user_current_index[user_id]
    
    await message.answer("✅ Данные обновлены! Теперь запросите новости заново.")

def register_user_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков пользователя"""
    logger.info("Регистрация обработчиков пользователя...")
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_fast_news, commands=["fast_news"])
    dp.register_message_handler(show_latest_news, commands=["news"])
    dp.register_message_handler(show_latest_news, lambda message: message.text == "📰 Последние новости")
    dp.register_message_handler(refresh_news, lambda message: message.text == "🔄 Обновить данные")
    logger.info("Обработчики пользователя зарегистрированы")