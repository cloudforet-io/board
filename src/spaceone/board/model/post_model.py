from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class Post(MongoModel):
    board_type = StringField(max_length=40)
    post_id = StringField(max_length=40, generate_id="post", unique=True)
    category = StringField(null=True, default=None)
    title = StringField(max_length=255)
    contents = StringField()
    options = DictField(default={})
    view_count = IntField(default=0)
    writer = StringField()
    files = ListField(StringField(), default=[])
    resource_group = StringField(max_length=40, choices=("SYSTEM", "DOMAIN"))
    domain_id = StringField(max_length=40)
    user_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": [
            "category",
            "title",
            "contents",
            "options",
            "writer",
            "files",
        ],
        "minimal_fields": [
            "board_type",
            "post_id",
            "category",
            "title",
            "resource_group",
            "domain_id",
        ],
        "ordering": ["-created_at"],
        "change_query_keys": {
            "is_pinned": "options.is_pinned",
            "is_popup": "options.is_popup"
        },
        "indexes": [
            "board_type",
            "category",
            "writer",
            "resource_group",
            "domain_id",
            "user_id",
        ],
    }
