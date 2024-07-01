import logging

from spaceone.core import cache
from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.auth.jwt.jwt_util import JWTUtil

_LOGGER = logging.getLogger(__name__)


class ConfigManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")
        self.config_conn: SpaceConnector = self.locator.get_connector(
            SpaceConnector, service="config"
        )

    @cache.cacheable(
        key="board:domain-config-settings:{domain_id}:settings", expire=300
    )
    def get_domain_config(self, domain_id: str):
        if self.token_type == "SYSTEM_TOKEN":
            response = self.config_conn.dispatch(
                "DomainConfig.get",
                {"name": "settings"},
                x_domain_id=domain_id,
            )
        else:
            response = self.config_conn.dispatch(
                "DomainConfig.get",
                {"name": "settings"},
            )
        return response
