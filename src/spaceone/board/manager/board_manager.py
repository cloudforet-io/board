import logging
from typing import Union
from spaceone.core.manager import BaseManager

from spaceone.board.model.board_model import Board
from spaceone.board.conf.board_conf import DEFAULT_BOARDS

_LOGGER = logging.getLogger(__name__)


class BoardManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board_model: Board = self.locator.get_model(Board)

    def create_board(self, params: dict) -> Board:
        def _rollback(vo: Board):
            _LOGGER.info(f"[create_board._rollback] " f"Delete board : {vo.name}")
            vo.delete()

        board_vo: Board = self.board_model.create(params)
        self.transaction.add_rollback(_rollback, board_vo)

        return board_vo

    def update_board(self, params: dict) -> Board:
        board_vo: Board = self.get_board(params["board_id"])
        return self.update_board_by_vo(params, board_vo)

    def update_board_by_vo(self, params: dict, board_vo: Board) -> Board:
        def _rollback(old_data: dict):
            _LOGGER.info(
                f"[update_board_by_vo._rollback] Revert Data : "
                f'{old_data["board_id"]}'
            )
            board_vo.update(old_data)

        self.transaction.add_rollback(_rollback, board_vo.to_dict())

        return board_vo.update(params)

    def delete_board(self, params: dict) -> None:
        board_vo: Board = self.get_board(params["board_id"])
        board_vo.delete()

    def get_board(self, board_id: str) -> Board:
        return self.board_model.get(board_id=board_id)

    def list_boards(self, query: Union[dict, None] = None):
        if query is None:
            query = {}
        return self.board_model.query(**query)

    def stat_boards(self, query: dict) -> dict:
        return self.board_model.stat(**query)

    def create_default_boards(self, installed_boards: list) -> None:
        for board_info in DEFAULT_BOARDS:
            if board_info["name"] not in installed_boards:
                _LOGGER.debug(f'Create default board: {board_info["name"]}')
                self.create_board(board_info)
