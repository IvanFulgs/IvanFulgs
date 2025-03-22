from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заблокировать", callback_data="ban")],
        [InlineKeyboardButton(text="Разблокировать", callback_data="unban")],
        [InlineKeyboardButton(text="Установить ник", callback_data="set_nick")],
        [InlineKeyboardButton(text="Список команд", callback_data="commands")],
        [InlineKeyboardButton(text="Стафф", callback_data="staff")]
    ])
