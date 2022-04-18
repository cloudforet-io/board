from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class PostOptions(EmbeddedDocument):
    is_pinned = BooleanField(default=False)
    is_popup = BooleanField(default=False)


class Post(MongoModel):
    board_id = StringField(max_length=40)
    post_id = StringField(max_length=40, generate_id='post', unique=True)
    category = StringField()
    title = StringField(max_length=255)
    contents = StringField()
    options = EmbeddedDocumentField(PostOptions, default=PostOptions)
    view_count = IntField(default=0)
    writer = StringField()
    scope = StringField(max_length=20, choices=('SYSTEM', 'DOMAIN'))
    domain_id = StringField(max_length=40, default=None, null=True)
    user_id = StringField(max_length=40)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        'updatable_fields': [
            'category',
            'title',
            'contents',
            'options',
            'writer',
        ],
        'minimal_fields': [
            'board_id',
            'post_id',
        ],
        'change_query_keys': {
            'user_domains': 'domain_id'
        },
        'ordering': [
            '-created_at'
        ],
        'indexes': [
            'board_id',
            'post_id',
            'category',
            'writer',
            'domain_id',
            'user_id'
        ]
    }
