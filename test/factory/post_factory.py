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
    files = [
        {
            'file_id': 'file-123546789012',
            'name': 'image1',
            'state': 'DONE',
            'scope': 'GLOBAL',
            'file_type': 'PNG',
            'upload_url': 'http://localhost:8080',
            'download_url': 'http://localhost:8100',
            'tags': {},
            'reference': {'resource_id': post_id, 'resource_type': 'board.Post'},
            'project_id': utils.generate_id('project'),
            'domain_id': domain_id,
        }
        # {
        #     'file_id': 'file-123546789013',
        #     'name': 'image1',
        #     'state': 'DONE',
        #     'scope': 'DOMAIN',
        #     'file_type': 'PNG',
        #     'upload_url': 'http://localhost:8080',
        #     'download_url': 'http://localhost:8100',
        #     'tags': {},
        #     'reference': {'resource_id': post_id, 'resource_type': 'board.Post'},
        #     'project_id': utils.generate_id('project'),
        #     'domain_id': domain_id,
        #     'created_at': factory.Faker('date_time')
        # },
        # {
        #     'file_id': 'file-123546789014',
        #     'name': 'image1',
        #     'state': 'DONE',
        #     'scope': 'DOMAIN',
        #     'file_type': 'PNG',
        #     'upload_url': 'http://localhost:8080',
        #     'download_url': 'http://localhost:8100',
        #     'tags': {},
        #     'reference': {'resource_id': post_id, 'resource_type': 'board.Post'},
        #     'project_id': utils.generate_id('project'),
        #     'domain_id': domain_id,
        #     'created_at': factory.Faker('date_time')
        # }
    ]
    created_at = factory.Faker('date_time')
    updated_at = factory.Faker('date_time')
