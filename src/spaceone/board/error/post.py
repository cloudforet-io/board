from spaceone.core.error import *


class ERROR_SETTING_CATEGORIES(ERROR_BASE):
    _message = 'First, you need to set the categories of the board.'


class ERROR_INVALID_CATEGORY(ERROR_BASE):
    _message = 'Invalid category (category = {category}), you must choose one of {categories}'


class ERROR_INVALID_KEY_IN_OPTIONS(ERROR_BASE):
    _message = 'Invalid key in options'


class ERROR_NOT_FOUND_FILE(ERROR_BASE):
    _message = '{file_id} does not exist in {domain_id}'


class ERROR_INVALID_FILE_STATE(ERROR_BASE):
    _message = 'file state is invalid (file_id = {file_id}, state = {state})'
