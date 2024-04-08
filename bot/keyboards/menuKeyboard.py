from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.callbacks.UserCallbackFactory import UserCallbackFactory
from bot.labels.buttons import DONT_DISTURB_BTN


def get_menu_keyboard(sku: int) -> InlineKeyboardMarkup:
    dont_disturb_cb = UserCallbackFactory(sku=sku).pack()
    keyboard = [
        [InlineKeyboardButton(text=DONT_DISTURB_BTN, callback_data=dont_disturb_cb)]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup
