from mongoengine import StringField, ListField, DictField, DateTimeField

from spaceone.core.model.mongo_model import MongoModel


class Board(MongoModel):
    board_id = StringField(max_length=40, generate_id='bo', unique=True)
    name = StringField(max_length=255, default='')
    categories = ListField(StringField(max_length=40))
    tags = DictField()
    created_at = DateTimeField(auto_now_add=True)

    meta = {
        'updatable_fields': [
            'name',
            'categories',
            'tags'
        ],
        'minimal_fields': [
            'board_id',
            'name',
            'categories'
        ],
        # 'change_query_keys': {},
        'ordering': [
            '-created_at'
        ],
        'indexes': [
            'board_id'
        ]
    }
