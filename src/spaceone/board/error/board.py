from spaceone.core.error import *


class ERROR_BOARD_CATEGORIES_NOT_ALLOW_EMPTY(ERROR_INVALID_ARGUMENT):
    _message = 'The board categories does not allow empty. (board_id = {board_id})'
