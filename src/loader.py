import telebot
from data.config import Config

# Инициализация бота
bot = telebot.TeleBot(Config.BOT_TOKEN, parse_mode='HTML')

__all__ = ['bot']
