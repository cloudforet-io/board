from spaceone.core.error import *


class ERROR_SETTING_CATEGORIES(ERROR_BASE):
    _message = 'First, you need to set the categories of the board.'


class ERROR_INVALID_CATEGORY(ERROR_BASE):
    _message = 'Invalid category (category = {category}), you must choose one of {categories}'
