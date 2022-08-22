from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class Post(MongoModel):
    board_id = StringField(max_length=40)
    post_id = StringField(max_length=40, generate_id='post', unique=True)
    post_type = StringField(max_length=20, choices=('SYSTEM', 'INTERNAL'))
    category = StringField(null=True, default=None)
    title = StringField(max_length=255)
    contents = StringField()
    options = DictField(default={})
    view_count = IntField(default=0)
    writer = StringField()
    files = ListField(StringField(), default=[])
    scope = StringField(max_length=20, choices=('PUBLIC', 'DOMAIN'))
    domain_id = StringField(max_length=40, default=None, null=True)
    user_id = StringField(max_length=40)
    user_domain_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'category',
            'title',
            'contents',
            'options',
            'writer',
            'files'
        ],
        'minimal_fields': [
            'board_id',
            'post_id',
            'post_type',
            'category',
            'title',
            'scope',
            'domain_id'
        ],
        'change_query_keys': {
            'user_domains': 'domain_id'
        },
        'ordering': [
            '-created_at'
        ],
        'indexes': [
            'board_id',
            'post_type',
            'category',
            'writer',
            'scope',
            'domain_id',
            'user_id',
            'user_domain_id'
        ]
    }
