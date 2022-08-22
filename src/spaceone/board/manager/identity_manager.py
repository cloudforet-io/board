import logging

from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector


_LOGGER = logging.getLogger(__name__)


class IdentityManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identity_connector: SpaceConnector = self.locator.get_connector('SpaceConnector', service='identity')

    def get_domain(self, domain_id):
        return self.identity_connector.dispatch('Domain.get', {'domain_id': domain_id})
