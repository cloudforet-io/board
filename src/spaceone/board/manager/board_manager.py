import logging
from spaceone.core.manager import BaseManager

from spaceone.board.model.board_model import Board

_LOGGER = logging.getLogger(__name__)


class BoardManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board_model: Board = self.locator.get_model('Board')

    def create_board(self, params):
        def _rollback(board_vo):
            _LOGGER.info(f'[create_board._rollback] '
                         f'Delete board : {board_vo.name}')
            board_vo.delete()

        board_vo: Board = self.board_model.create(params)
        self.transaction.add_rollback(_rollback, board_vo)

        return board_vo

    def update_board(self, params):
        board_vo: Board = self.get_board(params['board_id'])
        return self.update_board_by_vo(params, board_vo)

    def update_board_by_vo(self, params, board_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_board_by_vo._rollback] Revert Data : '
                         f'{old_data["board_id"]}')
            board_vo.update(old_data)

        self.transaction.add_rollback(_rollback, board_vo.to_dict())

        return board_vo.update(params)

    def delete_board(self, params):
        board_vo: Board = self.get_board(params['board_id'])
        board_vo.delete()

    def get_board(self, board_id, only=None):
        return self.board_model.get(board_id=board_id, only=only)

    def list_boards(self, query={}):
        return self.board_model.query(**query)

    def stat_boards(self, query):
        return self.board_model.stat(**query)
