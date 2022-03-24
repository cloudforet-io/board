from spaceone.core.service import *
from spaceone.board.manager.board_manager import BoardManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class BoardService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_rule_mgr: BoardManager = self.locator.get_manager('BoardManager')

    def create(self, params):
        pass

    def update(self, params):
        pass

    def set_categories(self, params):
        pass

    def delete(self, params):
        pass

    def get(self, params):
        pass

    def list(self, params):
        pass

    def stat(self, params):
        pass
