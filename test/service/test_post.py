import unittest
from unittest.mock import patch

from mongoengine import connect, disconnect
from spaceone.core import config, utils
from spaceone.core.transaction import Transaction
from spaceone.core.unittest.result import print_data

from spaceone.board.error import *
from spaceone.board.info import PostInfo, PostsInfo, StatisticsInfo
from spaceone.board.manager import BoardManager, PostManager
from spaceone.board.model import Post
from spaceone.board.service.post_service import PostService

from test.factory.board_factory import BoardFactory
from test.factory.post_factory import PostFactory


class TestPostService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.board')
        config.set_service_config()
        config.set_global(MOCK_MODE=True)
        connect('test', host='mongomock://localhost')

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'board',
            'api_class': 'Post',
            'user_id': utils.generate_id('user')
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all data_sources')
        post_vos = Post.objects.filter()
        post_vos.delete()

    def test_create_post(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'category': 'c',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kwon',
            'domain_id': self.domain_id,
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        post_vo = post_svc.create(params.copy())
        print(params['domain_id'])
        print_data(post_vo.to_dict(), 'test_create_post')
        PostInfo(post_vo)

        self.assertIsInstance(post_vo, Post)
        self.assertEqual(params['title'], post_vo.title)
        self.assertEqual(params['board_id'], post_vo.board_id)
        self.assertEqual(self.transaction.get_meta('user_id'), post_vo.user_id)
        print(post_vo.options)

    def test_create_post_none_category(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kwon',
            'domain_id': self.domain_id,
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        post_vo = post_svc.create(params.copy())
        print_data(post_vo.to_dict(), 'test_create_post')
        PostInfo(post_vo)

        self.assertIsInstance(post_vo, Post)
        self.assertEqual(params['title'], post_vo.title)
        self.assertEqual(params['board_id'], post_vo.board_id)
        self.assertEqual(self.transaction.get_meta('user_id'), post_vo.user_id)
        print(post_vo.options)

    def test_create_post_with_options_one_key(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'category': 'c',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': True
            },
            'writer': 'Kwon',
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'domain_id': self.domain_id,
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        post_vo = post_svc.create(params.copy())
        print(params['domain_id'])
        print_data(post_vo.to_dict(), 'test_create_post')
        PostInfo(post_vo)

        self.assertIsInstance(post_vo, Post)
        self.assertEqual(params['title'], post_vo.title)
        self.assertEqual(params['board_id'], post_vo.board_id)
        self.assertEqual(self.transaction.get_meta('user_id'), post_vo.user_id)
        print(post_vo.options)

    def test_create_post_invalid_options(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'category': 'c',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False,
                'is_check': True
            },
            'writer': 'Kwon',
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'domain_id': self.domain_id,
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        with self.assertRaises(ERROR_INVALID_KEY_IN_OPTIONS):
            post_svc.create(params.copy())

    def test_create_post_invalid_board_id(self):
        params = {
            'board_id': utils.generate_id('board'),
            'category': 'c',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kwon',
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'domain_id': self.domain_id,
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        with self.assertRaises(ERROR_NOT_FOUND):
            post_svc.create(params.copy())

    def test_create_post_valid_categories(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'category': 'a',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kwon',
            'domain_id': self.domain_id,
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        post_vo = post_svc.create(params.copy())

        print_data(post_vo.to_dict(), 'test_create_post')
        PostInfo(post_vo)

        self.assertIsInstance(post_vo, Post)
        self.assertEqual(params['title'], post_vo.title)
        self.assertEqual(params['board_id'], post_vo.board_id)
        self.assertEqual(self.transaction.get_meta('user_id'), post_vo.user_id)

    def test_create_post_empty_categories(self):
        board_vo = BoardFactory(categories=[])

        params = {
            'board_id': board_vo.board_id,
            'category': 'd',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kwon',
            'domain_id': self.domain_id,
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        with self.assertRaises(ERROR_INVALID_CATEGORY):
            post_svc.create(params.copy())

    def test_create_post_invalid_categories(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'category': 'd',
            'title': 'test sample',
            'contents': 'This is test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kwon',
            'domain_id': self.domain_id,
            'user_domain_id': self.transaction.get_meta("domain_id"),
            'user_id': utils.generate_id('user')
        }

        self.transaction.method = 'create'
        post_svc = PostService(transaction=self.transaction)
        with self.assertRaises(ERROR_INVALID_CATEGORY):
            post_svc.create(params.copy())

    def test_update_post(self):
        board_vo = BoardFactory()
        post_vo = PostFactory(board_id=board_vo.board_id,
                              domain_id=self.domain_id)

        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'category': 'a',
            'title': 'test param sample',
            'contents': 'test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kim',
            'domain_id': self.domain_id,
        }

        self.transaction.method = 'update'
        post_svc = PostService(transaction=self.transaction)

        update_post_vo = post_svc.update(params.copy())

        print_data(update_post_vo.to_dict(), 'test_update_post')
        PostInfo(update_post_vo)

        self.assertIsInstance(update_post_vo, Post)
        self.assertEqual(params['board_id'], update_post_vo.board_id)
        self.assertEqual(params['post_id'], update_post_vo.post_id)
        self.assertEqual(params['category'], update_post_vo.category)
        self.assertEqual(params['title'], update_post_vo.title)
        self.assertEqual(params['domain_id'], update_post_vo.domain_id)

    def test_update_post_options_invalid_options(self):
        board_vo = BoardFactory()
        options = {
            'is_pinned': False,
            'is_popup': True
        }
        post_vo = PostFactory(board_id=board_vo.board_id,
                              options=options,
                              domain_id=self.domain_id)
        print(post_vo.options)
        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'category': 'a',
            'title': 'test params sample',
            'contents': 'test sample of contents.',
            'options': {
                'is_pinned': False
            },
            'writer': 'Kim',
            'domain_id': post_vo.domain_id,
        }

        self.transaction.method = 'update'
        post_svc = PostService(transaction=self.transaction)

        update_post_vo = post_svc.update(params.copy())

        print_data(update_post_vo.to_dict(), 'test_update_post')
        PostInfo(update_post_vo)

        self.assertIsInstance(update_post_vo, Post)
        self.assertEqual(params['board_id'], update_post_vo.board_id)
        self.assertEqual(params['post_id'], update_post_vo.post_id)
        self.assertEqual(params['category'], update_post_vo.category)
        self.assertEqual(params['title'], update_post_vo.title)
        self.assertEqual(params['domain_id'], update_post_vo.domain_id)
        self.assertFalse(update_post_vo.options['is_pinned'])
        self.assertTrue(update_post_vo.options['is_popup'])

    def test_update_post_options_validation(self):
        board_vo = BoardFactory()
        options = {
            'is_pinned': False,
            'is_popup': True
        }
        post_vo = PostFactory(board_id=board_vo.board_id,
                              options=options,
                              domain_id=self.domain_id)

        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'category': 'a',
            'title': 'test params sample',
            'contents': 'test sample of contents.',
            'options': {
                'is_pinned': True,
                'is_popup': False
            },
            'writer': 'Kim',
            'domain_id': post_vo.domain_id,
        }

        self.transaction.method = 'update'
        post_svc = PostService(transaction=self.transaction)

        update_post_vo = post_svc.update(params.copy())

        print_data(update_post_vo.to_dict(), 'test_update_post')
        PostInfo(update_post_vo)

        self.assertIsInstance(update_post_vo, Post)
        self.assertEqual(params['board_id'], update_post_vo.board_id)
        self.assertEqual(params['post_id'], update_post_vo.post_id)
        self.assertEqual(params['category'], update_post_vo.category)
        self.assertEqual(params['title'], update_post_vo.title)
        self.assertEqual(params['domain_id'], update_post_vo.domain_id)
        self.assertTrue(update_post_vo.options['is_pinned'])
        self.assertFalse(update_post_vo.options['is_popup'])

    def test_update_post_options_none(self):
        board_vo = BoardFactory()
        options = {
            'is_pinned': True,
            'is_popup': True
        }
        post_vo = PostFactory(board_id=board_vo.board_id,
                              options=options,
                              domain_id=self.domain_id)

        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'category': 'a',
            'title': 'test params sample',
            'contents': 'test sample of contents.',
            'writer': 'Kim',
            'domain_id': post_vo.domain_id,
        }

        self.transaction.method = 'update'
        post_svc = PostService(transaction=self.transaction)

        update_post_vo = post_svc.update(params.copy())

        print_data(update_post_vo.to_dict(), 'test_update_post')
        PostInfo(update_post_vo)

        self.assertIsInstance(update_post_vo, Post)
        self.assertEqual(params['board_id'], update_post_vo.board_id)
        self.assertEqual(params['post_id'], update_post_vo.post_id)
        self.assertEqual(params['category'], update_post_vo.category)
        self.assertEqual(params['title'], update_post_vo.title)
        self.assertEqual(params['domain_id'], update_post_vo.domain_id)
        self.assertTrue(update_post_vo.options['is_pinned'])
        self.assertTrue(update_post_vo.options['is_popup'])

    def test_delete_post(self):
        post_vo = PostFactory(domain_id=self.domain_id)

        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'delete'
        post_svc = PostService(transaction=self.transaction)
        result = post_svc.delete(params)

        self.assertIsNone(result)

    def test_list_board(self):
        post_vos = PostFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), post_vos))

        print_data(post_vos[0].to_dict(), "1st board_vo")
        print_data(post_vos[4].to_dict(), "5th board_vo")

        params = {
            'board_id': post_vos[4].board_id,
            'post_id': post_vos[4].post_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'list'
        post_vos = PostService(transaction=self.transaction)
        post_svc_vos, total_count = post_vos.list(params)
        PostsInfo(post_svc_vos, total_count)

        self.assertEqual(len(post_svc_vos), 1)
        self.assertEqual(post_svc_vos[0].board_id, params.get('board_id'))
        self.assertEqual(post_svc_vos[0].post_id, params.get('post_id'))
        self.assertIsInstance(post_svc_vos[0], Post)
        self.assertEqual(total_count, 1)

    def test_increase_view_count(self):
        post_vo = PostFactory(domain_id=self.domain_id)

        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        post_svc = PostService(transaction=self.transaction)
        post_svc.get(params)
        get_post_vo = post_svc.get(params)

        print_data(get_post_vo.to_dict(), 'test_get_post')

    def test_get_post(self):
        post_vo = PostFactory(domain_id=self.domain_id)
        params = {
            'board_id': post_vo.board_id,
            'post_id': post_vo.post_id,
            'domain_id': self.domain_id
        }

        self.transaction.method = 'get'
        post_svc = PostService(transaction=self.transaction)
        get_post_vo = post_svc.get(params)

        print_data(get_post_vo.to_dict(), 'test_get_post')
        PostInfo(get_post_vo)

        self.assertIsInstance(get_post_vo, Post)

    def test_stat_post(self):
        post_vos = PostFactory.build_batch(10, domain_id=self.domain_id)
        list(map(lambda vo: vo.save(), post_vos))

        params = {
            'domain_id'
        }


if __name__ == '__main__':
    unittest.main()
