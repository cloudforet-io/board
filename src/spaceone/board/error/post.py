from spaceone.core.error import *


class ERROR_INVALID_KEY_IN_OPTIONS(ERROR_INVALID_ARGUMENT):
    _message = "Invalid key in options. (key = {key})"


class ERROR_INVALID_FILE_STATE(ERROR_INVALID_ARGUMENT):
    _message = "File state is invalid (file_id = {file_id}, state = {state})"


class ERROR_NOT_CHANGE_WORKSPACE(ERROR_INVALID_ARGUMENT):
    _message = ("Workspace changes are allowed only when resource_group is WORKSPACE. "
                "(post_resource_group = {resource_group})")
