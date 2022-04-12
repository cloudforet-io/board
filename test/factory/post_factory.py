import factory

from spaceone.core import utils

from spaceone.board.model import Post


class PostFactory(factory.mongoengine.MongoEngineFactory):
    class Meta:
        model = Post

    board_id = factory.LazyAttribute(lambda o: utils.generate_id('board'))
    post_id = factory.LazyAttribute(lambda o: utils.generate_id('post'))
    category = 'notice'
    title = 'title sample'
    contents = 'This is test sample of contents.'
    options = {
        'is_pinned': False,
        'is_popup': False
    }
    view_count = 0
    writer = 'Kwon'
    scope = 'DOMAIN'
    domain_id = utils.generate_id('domain')
    created_at = factory.Faker('date_time')
    updated_at = factory.Faker('date_time')
