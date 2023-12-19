from spaceone.core.error import *


class ERROR_INVALID_KEY_IN_OPTIONS(ERROR_BASE):
    _message = "Invalid key in options"


class ERROR_INVALID_FILE_STATE(ERROR_BASE):
    _message = "file state is invalid (file_id = {file_id}, state = {state})"
