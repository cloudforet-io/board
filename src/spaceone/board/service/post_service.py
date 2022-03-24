from spaceone.core.service import *
from spaceone.board.manager.post_manager import PostManager


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class PostService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_mgr: PostManager = self.locator.get_manager('PostManager')

    def create(self, params):
        pass

    def update(self, params):
        pass

    def send_notification(self, params):
        pass

    def delete(self, params):
        pass

    def get(self, params):
        pass

    def list(self, params):
        pass

    def stat(self, params):
        pass
