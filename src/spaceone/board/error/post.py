from spaceone.core.error import *


class ERROR_INVALID_KEY_IN_OPTIONS(ERROR_INVALID_ARGUMENT):
    _message = "Invalid key in options. (key = {key})"


class ERROR_INVALID_FILE_STATE(ERROR_INVALID_ARGUMENT):
    _message = "File state is invalid (file_id = {file_id}, state = {state})"


class ERROR_NOT_CHANGE_WORKSPACE(ERROR_INVALID_ARGUMENT):
    _message = (
        "Workspace changes are allowed only when resource_group is WORKSPACE. "
        "(post_resource_group = {resource_group})"
    )


class ERROR_SMTP_CONNECTION_FAILED(ERROR_UNKNOWN):
    _message = "SMTP server connection failed. Please contact the administrator."


class ERROR_NOTICE_EMAIL_ALREADY_SENT(ERROR_UNKNOWN):
    _message = "Notice email has already been sent. please try again later. (post_id = {post_id})"
