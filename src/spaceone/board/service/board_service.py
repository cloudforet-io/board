import logging

from spaceone.core.service import *
from spaceone.board.manager.board_manager import BoardManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class BoardService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board_mgr: BoardManager = self.locator.get_manager('BoardManager')

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @check_required(['name'])
    def create(self, params):
        """Create board

        Args:
            params (dict): {
                'name': 'str',
                'categories': 'list',
                'tags': 'dict'
            }

        Returns:
            board_vo (object)
        """

        return self.board_mgr.create_board(params)

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @check_required(['board_id'])
    def update(self, params):
        """Update board

                Args:
                    params (dict): {
                        'board_id': 'str,
                        'name': 'str,
                        'tags': 'dict'
                    }

                Returns:
                    board_vo (object)
                """
        return self.board_mgr.update_board(params)

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @check_required(['board_id'])
    def set_categories(self, params):
        """Create board

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'categories': 'list'
                    }

                Returns:
                    board_vo (object)
                """

        params['categories'] = params.get('categories', [])

        return self.board_mgr.update_board(params)

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @check_required(['board_id'])
    def delete(self, params):
        """Delete board

                Args:
                    params (dict): {
                        'webhook_id': 'str',
                    }

                Returns:
                    None
                """

        self.board_mgr.delete_board(params)

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @check_required(['board_id'])
    def get(self, params):
        """Get board

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'only': 'list'
                    }

                Returns:
                    board_vo (object)
                """

        return self.board_mgr.get_board(params['board_id'])

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @append_query_filter(['board_id', 'name'])
    def list(self, params):
        """List boards

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'name': 'str',
                        'query': 'dict'
                    }

                Returns:
                    board_vos (object)
                    total_count
                """

        query = params.get('query', {})
        return self.board_mgr.list_boards(query)

    @transaction(append_meta={'authorization.scope': 'PUBLIC'})
    @check_required(['query'])
    def stat(self, params):
        """Stat boards

                Args:
                    params (dict): {
                        'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
                    }

                Returns:
                    values (list) : 'list of statistics data'
                """

        query = params.get('query', {})
        return self.board_mgr.stat_boards(query)
