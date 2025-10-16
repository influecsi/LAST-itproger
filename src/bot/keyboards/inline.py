from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_article_keyboard(article_url: str, current_index: int, total_articles: int):
    """Клавиатура для навигации по статьям"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    full_content_btn = InlineKeyboardButton(
        text="📖 Полный текст",
        callback_data=f"full_content:{article_url}"
    )

    next_btn = InlineKeyboardButton(
        text="➡️ Следующая",
        callback_data=f"next_article:{(current_index + 1) % total_articles}"
    )

    prev_btn = InlineKeyboardButton(
        text="⬅️ Предыдущая",
        callback_data=f"next_article:{(current_index - 1) % total_articles}"
    )

    keyboard.add(prev_btn, next_btn)
    keyboard.add(full_content_btn)

    return keyboard


def get_pagination_keyboard(page: int, has_next: bool = True):
    """Клавиатура для пагинации"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"page:{page-1}"
        ))

    if has_next:
        buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"page:{page+1}"
        ))

    keyboard.add(*buttons)

    return keyboard
