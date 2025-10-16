from aiogram import executor
from loader import dp, bot
import logging

# Включаем логирование
logging.basicConfig(level=logging.INFO)

async def on_startup(dp):
    try:
        bot_info = await bot.get_me()
        print(f"✅ Бот {bot_info.username} успешно запущен!")
        print("✅ Бот готов к работе...")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

async def on_shutdown(dp):
    print("Бот выключается...")

if __name__ == "__main__":
    print("Запуск бота...")
    
    # Импортируем обработчики после создания dp
    from bot.handlers import user_handlers, callback_handlers
    
    # Регистрируем обработчики
    user_handlers.register_user_handlers(dp)
    callback_handlers.register_callback_handlers(dp)
    
    executor.start_polling(
        dp, 
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )