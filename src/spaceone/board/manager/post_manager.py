import logging

from spaceone.core.manager import BaseManager
from spaceone.board.model import Post

_LOGGER = logging.getLogger(__name__)


class PostManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_model: Post = self.locator.get_model('Post')

    def create_board(self, params):
        def _rollback(post_vo):
            _LOGGER.info(f'[create_post._rollback] '
                         f'Delete post : {post_vo.name}')
            post_vo.delete()

        post_vo: Post = self.post_model.create(params)
        self.transaction.add_rollback(_rollback, post_vo)

        return post_vo

    def update_post(self, params):
        post_vo: Post = self.get_post(params['board_id'], params['post_id'])
        return self.update_post_by_vo(params, post_vo)

    def update_post_by_vo(self, params, post_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_post_by_vo._rollback] Revert Data : '
                         f'{old_data["post_id"]}')
            post_vo.update(old_data)

        self.transaction.add_rollback(_rollback, post_vo.to_dict())

        return post_vo.update(params)

    def get_post(self, board_id, post_id, only=None):
        return self.post_model.get(board_id=board_id, post_id=post_id, only=only)

    def list_boards(self, query={}):
        return self.post_model.query(**query)

    def stat_boards(self, query):
        return self.post_model.stat(**query)

    @staticmethod
    def increase_view_count(post_vo):
        post_vo.increment("view_count")

    @staticmethod
    def delete_post_vo(post_vo):
        post_vo.delete()
