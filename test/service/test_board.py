import unittest

from mongoengine import connect, disconnect
from spaceone.core import config, utils
from spaceone.core.transaction import Transaction
from spaceone.core.unittest.result import print_data

from spaceone.board.info import BoardInfo, BoardsInfo, StatisticsInfo
from spaceone.board.model import Board
from spaceone.board.service.board_service import BoardService
from test.factory.board_factory import BoardFactory


class TestBoardService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.board')
        config.set_service_config()
        config.set_global(MOCK_MODE=True)
        connect('test', host='mongomock://localhost')

        cls.domain_id = utils.generate_id('domain')
        cls.transaction = Transaction({
            'service': 'board',
            'api_class': 'Board'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        disconnect()

    def tearDown(self, *args) -> None:
        print()
        print('(tearDown) ==> Delete all data_sources')
        board_vos = Board.objects.filter()
        board_vos.delete()

    def test_create_board_required_param(self):
        params = {
            'name': 'Notice'
        }

        self.transaction.method = 'create'
        board_svc = BoardService(transaction=self.transaction)
        board_vo = board_svc.create(params.copy())

        print_data(board_vo.to_dict(), 'test_create_board')
        BoardInfo(board_vo)

        self.assertIsInstance(board_vo, Board)
        self.assertEqual(params['name'], board_vo.name)

    def test_create_board_params(self):
        params = {
            'name': 'Notice',
            'categories': ['a', 'b', 'c'],
            'tags': {
                'test': 'a'
            }
        }

        self.transaction.method = 'create'
        board_svc = BoardService(transaction=self.transaction)
        board_vo = board_svc.create(params.copy())

        print_data(board_vo.to_dict(), 'test_create_board_params_all')
        BoardInfo(board_vo)

        self.assertIsInstance(board_vo, Board)
        self.assertEqual(params['name'], board_vo.name)
        self.assertEqual(params['categories'], board_vo.categories)
        self.assertEqual(params['tags'], board_vo.tags)

    def test_create_invalid_params(self):
        params = {
            'categories': ['a', 'b', 'c']
        }

        self.transaction.method = 'create'
        board_svc = BoardService(transaction=self.transaction)
        with self.assertRaises(Exception):
            board_svc.create(params.copy())

    def test_update_board(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'name': 'new',
            'tags': {'a': 'b'}
        }

        self.transaction.method = 'update'
        board_svc = BoardService(transaction=self.transaction)
        update_board_vo = board_svc.update(params.copy())

        print_data(update_board_vo.to_dict(), 'test_update_board')
        BoardInfo(update_board_vo)

        self.assertIsInstance(update_board_vo, Board)
        self.assertEqual(params['board_id'], update_board_vo.board_id)
        self.assertEqual(params['name'], update_board_vo.name)
        self.assertEqual(params['tags'], update_board_vo.tags)

    def test_set_categories(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id,
            'categories': ['d', 'e', 'f']
        }

        self.transaction.method = 'set_categories'
        board_svc = BoardService(transaction=self.transaction)
        changed_categories_board_vo = board_svc.set_categories(params.copy())

        print_data(changed_categories_board_vo.to_dict(), 'test_changed_categories_board_vo')
        BoardInfo(changed_categories_board_vo)

        self.assertIsInstance(changed_categories_board_vo, Board)
        self.assertEqual(params['board_id'], changed_categories_board_vo.board_id)
        self.assertEqual(params['categories'], changed_categories_board_vo.categories)

    def test_delete_board(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id
        }

        self.transaction.method = 'delete'
        board_svc = BoardService(transaction=self.transaction)
        result = board_svc.delete(params)

        self.assertIsNone(result)

    def test_get_board(self):
        board_vo = BoardFactory()

        params = {
            'board_id': board_vo.board_id
        }

        self.transaction.method = 'get'
        board_svc = BoardService(transaction=self.transaction)
        get_board_vo = board_svc.get(params)

        print_data(get_board_vo.to_dict(), 'test_get_board')
        BoardInfo(get_board_vo)

        self.assertIsInstance(get_board_vo, Board)

    def test_list_board(self):
        board_vos = BoardFactory.build_batch(10)
        list(map(lambda vo: vo.save(), board_vos))

        print_data(board_vos[4].to_dict(), "5th board_vo")

        params = {
            'board_id': board_vos[4].board_id
        }

        self.transaction.method = 'list'
        board_svc = BoardService(transaction=self.transaction)
        board_svc_vos, total_count = board_svc.list(params)
        BoardsInfo(board_svc_vos, total_count)

        self.assertEqual(len(board_svc_vos), 1)
        self.assertEqual(board_svc_vos[0].board_id, params.get('board_id'))
        self.assertIsInstance(board_svc_vos[0], Board)
        self.assertEqual(total_count, 1)

    def test_stat_board(self):
        board_vos = BoardFactory.build_batch(10)
        list(map(lambda vo: vo.save(), board_vos))

        check_sample_board_vos = board_vos[0:3]
        check_sample_board_ids = []
        for board_vo in check_sample_board_vos:
            check_sample_board_ids.append(board_vo.board_id)

        params = {
            'query': {
                'distinct': 'board_id',
                'page': {
                    'start': 0,
                    'limit': 3
                }
            }
        }

        self.transaction.method = 'stat'
        board_svc = BoardService(transaction=self.transaction)
        values = board_svc.stat(params)
        StatisticsInfo(values)

        print_data(values, 'test_stat_board')


if __name__ == '__main__':
    unittest.main()
