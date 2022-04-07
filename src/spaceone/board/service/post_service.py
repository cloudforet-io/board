import logging

from spaceone.core.service import *
from spaceone.board.error import *

from spaceone.board.manager import PostManager, BoardManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class PostService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_mgr: PostManager = self.locator.get_manager('PostManager')
        self.board_mgr: BoardManager = self.locator.get_manager('BoardManager')

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'title', 'contents', 'user_id'])
    def create(self, params):
        """Create post

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'category': 'str',
                        'title': 'str',
                        'contents': 'str',
                        'options': 'dict',
                        'writer': 'str',
                        'domain_id': 'str',
                        'user_id': 'str'(meta)
                    }

                Returns:
                    post_vo (object)
        """
        board_id = params['board_id']
        params['user_id'] = self.transaction.get_meta('user_id')
        domain_id = params.get('domain_id')

        if domain_id:
            params['scope'] = 'DOMAIN'
        else:
            params['scope'] = 'SYSTEM'

        board_vo = self.board_mgr.get_board(board_id)
        categories = board_vo.categories

        if category := params.get('category'):
            if category not in categories:
                raise ERROR_INVALID_CATEGORY(category=category, categories=categories)

        return self.post_mgr.create_board(params)

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id', 'domain_id'])
    def update(self, params):
        """Update post

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'post_id': 'str',
                        'category': 'str',
                        'title': 'str',
                        'contents': 'str',
                        'options': 'dict',
                        'writer': 'str',
                        'domain_id': 'str'
                    }

                Returns:
                    post_vo (object)
        """

        post_vo = self.post_mgr.get_post(params['board_id'], params['post_id'], params['domain_id'])

        if category := params.get('category'):
            board_vo = self.board_mgr.get_board(params['board_id'])

            if category not in board_vo.categories:
                raise ERROR_INVALID_CATEGORY(category=category, categories=board_vo.categories)

        if options := params.get('options'):
            if 'is_pinned' not in options.keys():
                options.update({'is_pinned': post_vo.options.is_pinned})
            if 'is_popup' not in options.keys():
                options.update({'is_popup': post_vo.options.is_popup})

        return self.post_mgr.update_post_by_vo(params, post_vo)

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id'])
    def send_notification(self, params):
        pass

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id', 'domain_id'])
    def delete(self, params):
        """Delete post

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'post_id': 'str',
                        'domain_id': 'str'
                    }

                Returns:
                    post_vo (object)
        """

        board_id = params['board_id']
        post_id = params['post_id']
        domain_id = params['domain_id']

        post_vo = self.post_mgr.get_post(board_id, post_id, domain_id)

        self.post_mgr.delete_post_vo(post_vo)

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id', 'domain_id'])
    def get(self, params):
        """Get post

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'post_id': 'str',
                        'domain_id': 'str,
                        'only': 'list'
                    }

                Returns:
                    post_vo (object)
        """

        board_id = params['board_id']
        post_id = params['post_id']
        domain_id = params['domain_id']

        post_vo = self.post_mgr.get_post(board_id, post_id, domain_id, params.get('only'))

        self._increase_view_count(post_vo)

        return post_vo

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'domain_id'])
    @append_query_filter(['post_id', 'category', 'writer', 'user_id'])
    def list(self, params):
        """List posts

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'post_id': 'str',
                        'category': 'str',
                        'writer': 'str',
                        'user_id': 'str',
                        'domain_id': 'str',
                        'query': 'dict'
                    }

                Returns:
                    posts_vo (object)
                    total_count
        """

        params['domain_id'] = self.transaction.get_meta('domain_id')

        query = params.get('query', {})
        return self.post_mgr.list_boards(query)

    @transaction(append_meta={
        'authorization.scope': 'DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['query', 'domain_id'])
    def stat(self, params):
        """List posts

                Args:
                    params (dict): {
                        'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
                    }

                Returns:
                    values (list) : 'list of statistics data'
        """

        query = params.get('query', {})
        return self.post_mgr.stat_boards(query)

    def _increase_view_count(self, post_vo):
        params = {
            'view_count': post_vo.view_count + 1
        }

        self.post_mgr.update_post_by_vo(params, post_vo)
