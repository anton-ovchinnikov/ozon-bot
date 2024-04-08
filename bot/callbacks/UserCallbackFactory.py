from enum import Enum

from aiogram.filters.callback_data import CallbackData


class UserCallbackFactory(CallbackData, prefix='user'):
    sku: int
