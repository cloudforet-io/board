import logging

from spaceone.core import cache
from spaceone.core import config
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector
from spaceone.core.auth.jwt.jwt_util import JWTUtil

_LOGGER = logging.getLogger(__name__)


class IdentityManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.transaction.get_meta("token")
        self.token_type = JWTUtil.get_value_from_token(token, "typ")
        self.identity_conn: SpaceConnector = self.locator.get_connector(
            SpaceConnector, service="identity"
        )

    def list_users(self, domain_id: str, params: dict) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_conn.dispatch(
                "User.list", params, x_domain_id=domain_id
            )
        else:
            return self.identity_conn.dispatch("User.list", params)

    def list_workspaces(self, params: dict, domain_id: str) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_conn.dispatch(
                "Workspace.list", params, x_domain_id=domain_id
            )
        else:
            return self.identity_conn.dispatch("Workspace.list", params)

    def list_workspace_users(
        self, params: dict, domain_id: str, workspace_id: str
    ) -> dict:
        if self.token_type == "SYSTEM_TOKEN":
            return self.identity_conn.dispatch(
                "WorkspaceUser.list",
                params,
                x_domain_id=domain_id,
                x_workspace_id=workspace_id,
            )
        else:
            return self.identity_conn.dispatch("WorkspaceUser.list", params)

    def list_domains(self, params: dict) -> dict:
        system_token = config.get_global("TOKEN")
        return self.identity_conn.dispatch("Domain.list", params, token=system_token)
