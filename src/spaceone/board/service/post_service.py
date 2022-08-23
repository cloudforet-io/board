import copy
import logging

from spaceone.core.service import *
from spaceone.board.error import *

from spaceone.board.manager.post_manager import PostManager
from spaceone.board.manager.board_manager import BoardManager
from spaceone.board.manager.file_manager import FileManager
from spaceone.board.manager.identity_manager import IdentityManager

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
        self.file_mgr = None

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'title', 'contents'])
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
                        'files' : 'list',
                        'domain_id': 'str',
                        'user_id': 'str'(meta)
                    }

                Returns:
                    post_vo (object)
        """
        board_id = params['board_id']
        domain_id = params.get('domain_id')
        params['user_id'] = self.transaction.get_meta('user_id')
        params['user_domain_id'] = self.transaction.get_meta('domain_id')
        params['post_type'] = 'SYSTEM'

        file_ids = params.get('files', [])

        if domain_id:
            # If the post is not written in the root domain, set it to INTERNAL post_type
            identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')
            user_domain_info = identity_mgr.get_domain(params['user_domain_id'])

            if user_domain_info['name'] != 'root':
                params['post_type'] = 'INTERNAL'

            params['scope'] = 'DOMAIN'
        else:
            params['scope'] = 'PUBLIC'

        board_vo = self.board_mgr.get_board(board_id)
        categories = board_vo.categories

        if category := params.get('category'):
            if category not in categories:
                raise ERROR_INVALID_CATEGORY(category=category, categories=categories)

        _options = {'is_pinned': False, 'is_popup': False}

        if options := params.get('options', {}):
            self._valid_options(options)

            if 'is_pinned' in options:
                _options.update({'is_pinned': options['is_pinned']})
            if 'is_popup' in options:
                _options.update({'is_popup': options['is_popup']})

        params['options'] = _options

        self.file_mgr: FileManager = self.locator.get_manager('FileManager')
        self._check_files(file_ids, domain_id)
        post_vo = self.post_mgr.create_board(params)

        self._update_file_reference(post_vo.post_id, file_ids, domain_id)

        return post_vo

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id'])
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
                        'files' : 'list',
                        'domain_id': 'str'
                    }

                Returns:
                    post_vo (object)
        """

        domain_id = params.get('domain_id')
        post_vo = self.post_mgr.get_post(params['board_id'], params['post_id'])

        if category := params.get('category'):
            board_vo = self.board_mgr.get_board(params['board_id'])

            if category not in board_vo.categories:
                raise ERROR_INVALID_CATEGORY(category=category, categories=board_vo.categories)

        if options := params.get('options', {}):
            self._valid_options(options)

            _options = copy.deepcopy(post_vo.options)
            _options.update(options)

            params['options'] = _options

        if 'files' in params:
            self.file_mgr: FileManager = self.locator.get_manager('FileManager')

            new_file_ids = set(params['files'])
            old_file_ids = set(post_vo.files)

            if new_file_ids != old_file_ids:
                file_ids_to_be_deleted = list(old_file_ids - new_file_ids)
                file_ids_to_be_created = list(new_file_ids - old_file_ids)

                if len(file_ids_to_be_created) > 0:
                    self._check_files(file_ids_to_be_created, domain_id)
                    self._update_file_reference(post_vo.post_id, file_ids_to_be_created, domain_id)

                if len(file_ids_to_be_deleted) > 0:
                    for file_id in file_ids_to_be_deleted:
                        self.file_mgr.delete_file(file_id, domain_id)

        return self.post_mgr.update_post_by_vo(params, post_vo)

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id'])
    def send_notification(self, params):
        pass

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN',
        'authorization.require_domain_id': True
    })
    @check_required(['board_id', 'post_id'])
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
        domain_id = params.get('domain_id')

        post_vo = self.post_mgr.get_post(board_id, post_id)

        if len(post_vo.files) > 0:
            self.file_mgr: FileManager = self.locator.get_manager('FileManager')

            for file_id in post_vo.files:
                self.file_mgr.delete_file(file_id, domain_id)

        self.post_mgr.delete_post_vo(post_vo)

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN'
    })
    @check_required(['board_id', 'post_id'])
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
        domain_id = params.get('domain_id')

        post_vo = self.post_mgr.get_post(board_id, post_id, params.get('only'))
        self.post_mgr.increase_view_count(post_vo)

        self.file_mgr: FileManager = self.locator.get_manager('FileManager')

        files_info = []
        if len(post_vo.files) > 0:
            files_info = self._get_files_info_from_file_manager(post_vo.files, domain_id)

        return post_vo, files_info

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN'
    })
    @check_required(['board_id'])
    @append_query_filter(['board_id', 'post_id', 'post_type', 'category', 'writer', 'scope', 'user_id',
                          'user_domain_id', 'domain_id', 'user_domains'])
    def list(self, params):
        """List posts

                Args:
                    params (dict): {
                        'board_id': 'str',
                        'post_id': 'str',
                        'post_type': 'str',
                        'category': 'str',
                        'scope': 'str',
                        'writer': 'str',
                        'user_id': 'str',
                        'domain_id': 'str',
                        'query': 'dict',
                        'user_domains': 'list' // from meta
                    }

                Returns:
                    posts_vo (object)
                    total_count
        """

        query = params.get('query', {})
        return self.post_mgr.list_boards(query)

    @transaction(append_meta={
        'authorization.scope': 'PUBLIC_OR_DOMAIN'
    })
    @check_required(['query'])
    @append_query_filter(['user_domains'])
    def stat(self, params):
        """List posts

                Args:
                    params (dict): {
                        'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                        'user_domains': 'list' // from meta
                    }

                Returns:
                    values (list) : 'list of statistics data'
        """

        query = params.get('query', {})
        return self.post_mgr.stat_boards(query)

    def _check_files(self, file_ids, domain_id):
        for file_id in file_ids:
            self._verify_file(file_id, domain_id)

    def _update_file_reference(self, post_id, files, domain_id):
        for file in files:
            reference = {'resource_id': post_id, 'resource_type': 'board.Post'}
            self.file_mgr.update_file_reference(file, reference, domain_id)

    def _verify_file(self, file_id, domain_id):
        file_info = self.file_mgr.get_file(file_id, domain_id)

        file_state = file_info.get('state')
        if file_state != 'DONE':
            raise ERROR_INVALID_FILE_STATE(file_id=file_id, state=file_state)

    def _get_files_info_from_file_manager(self, file_ids, domain_id):
        files_info = []
        for file_id in file_ids:
            file_info = self.file_mgr.get_download_url(file_id, domain_id)
            files_info.append(file_info)
        return files_info

    @staticmethod
    def _valid_options(options):
        exact_keys = ['is_pinned', 'is_popup']

        for key in options:
            if key not in exact_keys:
                raise ERROR_INVALID_KEY_IN_OPTIONS
