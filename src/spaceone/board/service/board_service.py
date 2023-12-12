import logging

from spaceone.core import cache
from spaceone.core.service import *
from spaceone.board.manager.board_manager import BoardManager
from spaceone.board.model.board_model import Board

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class BoardService(BaseService):
    service = "board"
    resource = "Board"
    permission_group = "GLOBAL"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.board_mgr: BoardManager = self.locator.get_manager(BoardManager)

    @transaction(scope="admin:write")
    @check_required(["name"])
    def create(self, params: dict) -> Board:
        """Create board

        Args:
            params (dict): {
                'name': 'str',          # required
                'categories': 'list',
                'tags': 'dict'
            }

        Returns:
            board_vo (object)
        """

        return self.board_mgr.create_board(params)

    @transaction(scope="admin:write")
    @check_required(["board_id"])
    def update(self, params: dict) -> Board:
        """Update board

        Args:
            params (dict): {
                'board_id': 'str,    # required
                'name': 'str,
                'tags': 'dict'
            }

        Returns:
            board_vo (object)
        """
        return self.board_mgr.update_board(params)

    @transaction(scope="admin:write")
    @check_required(["board_id"])
    def set_categories(self, params: dict) -> Board:
        """Create board

        Args:
            params (dict): {
                'board_id': 'str',    # required
                'categories': 'list'  # required
            }

        Returns:
            board_vo (object)
        """

        params["categories"] = params.get("categories", [])

        return self.board_mgr.update_board(params)

    @transaction(scope="admin:write")
    @check_required(["board_id"])
    def delete(self, params: dict) -> None:
        """Delete board

        Args:
            params (dict): {
                'board_id': 'str',    # required
            }

        Returns:
            None
        """

        self.board_mgr.delete_board(params)

    @transaction(scope="workspace_member:write")
    @check_required(["board_id"])
    def get(self, params: dict) -> Board:
        """Get board

        Args:
            params (dict): {
                'board_id': 'str'    # required
            }

        Returns:
            board_vo (object)
        """

        return self.board_mgr.get_board(params["board_id"])

    @transaction(scope="workspace_member:write")
    @append_query_filter(["board_id", "name"])
    def list(self, params: dict) -> dict:
        """List boards

        Args:
            params (dict): {
                'query': 'dict'
                'board_id': 'str',
                'name': 'str'
            }

        Returns:
            board_vos (object)
            total_count
        """

        query = params.get("query", {})
        self._create_default_board()

        return self.board_mgr.list_boards(query)

    @transaction(scope="workspace_member:write")
    @check_required(["query"])
    def stat(self, params: dict) -> dict:
        """Stat boards

        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'    # required
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.get("query", {})
        return self.board_mgr.stat_boards(query)

    @cache.cacheable(key="board:default:init", expire=300)
    def _create_default_board(self) -> bool:
        board_vos, total_count = self.board_mgr.list_boards()
        installed_boards = [board_vo.name for board_vo in board_vos]
        self.board_mgr.create_default_boards(installed_boards)

        return True
