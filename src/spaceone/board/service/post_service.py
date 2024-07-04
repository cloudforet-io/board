import copy
import logging
from typing import Tuple

from spaceone.core import config, cache
from spaceone.core.service import *

from spaceone.board.error import *
from spaceone.board.manager.config_manager import ConfigManager
from spaceone.board.manager.email_manager import EmailManager
from spaceone.board.manager.post_manager import PostManager
from spaceone.board.manager.file_manager import FileManager
from spaceone.board.manager.identity_manager import IdentityManager
from spaceone.board.model.post_model import Post

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class PostService(BaseService):
    resource = "Post"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_mgr: PostManager = self.locator.get_manager(PostManager)
        self.file_mgr = None
        self.identity_mgr = None
        self.config_mgr = None

    @transaction(
        permission="board:Post.write",
        role_types=["SYSTEM_ADMIN", "DOMAIN_ADMIN"],
    )
    @check_required(["board_type", "title", "contents"])
    def create(self, params: dict) -> Post:
        """Create post

        Args:
            params (dict): {
                'board_type': 'str',        # required
                'category': 'str',
                'title': 'str',             # required
                'contents': 'str',          # required
                'files' : 'list',
                'options': 'dict',
                'writer': 'str',
                'workspaces': 'list',       # required
                'resource_group': 'str',    # required
                'domain_id': 'str',         # injected from auth
                'user_id': 'str'            # injected from auth
            }

        Returns:
            post_vo (object)
        """

        resource_group = params["resource_group"]
        if resource_group == "SYSTEM":
            params["domain_id"] = "*"
            params["workspaces"] = ["*"]
        elif resource_group == "DOMAIN":
            if not params.get("domain_id"):
                raise ERROR_REQUIRED_PARAMETER(key="domain_id")

            params["workspaces"] = ["*"]
        else:
            if not params.get("workspaces"):
                raise ERROR_REQUIRED_PARAMETER(key="workspaces")

        _options = {"is_pinned": False, "is_popup": False}
        if options := params.get("options", {}):
            self._valid_options(options)

            if "is_pinned" in options:
                _options.update({"is_pinned": options["is_pinned"]})
            if "is_popup" in options:
                _options.update({"is_popup": options["is_popup"]})
        params["options"] = _options

        file_ids = params.get("files", [])
        self.file_mgr: FileManager = self.locator.get_manager(FileManager)
        self._check_files(file_ids)
        post_vo = self.post_mgr.create_post(params)

        self._update_file_reference(post_vo.post_id, file_ids)

        return post_vo

    @transaction(
        permission="board:Post.write",
        role_types=["SYSTEM_ADMIN", "DOMAIN_ADMIN"],
    )
    @check_required(["post_id"])
    def update(self, params: dict) -> Post:
        """Update post

        Args:
            params (dict): {
                'post_id': 'str',           # required
                'category': 'str',
                'title': 'str',
                'contents': 'str',
                'files' : 'list',
                'options': 'dict',
                'writer': 'str',
                'workspaces': 'list',
                'domain_id': 'str',         # injected from auth
            }

        Returns:
            post_vo (object)
        """

        post_id = params["post_id"]
        domain_id = params.get("domain_id")

        post_vo = self.post_mgr.get_post(post_id, domain_id)

        if "workspaces" in params:
            if post_vo.resource_group != "WORKSPACE":
                raise ERROR_NOT_CHANGE_WORKSPACE(resource_group=post_vo.resource_group)

        if options := params.get("options", {}):
            self._valid_options(options)

            _options = copy.deepcopy(post_vo.options)
            _options.update(options)

            params["options"] = _options

        if "files" in params:
            self.file_mgr: FileManager = self.locator.get_manager(FileManager)

            new_file_ids = set(params["files"])
            old_file_ids = set(post_vo.files)

            if new_file_ids != old_file_ids:
                file_ids_to_be_deleted = list(old_file_ids - new_file_ids)
                file_ids_to_be_created = list(new_file_ids - old_file_ids)

                if len(file_ids_to_be_created) > 0:
                    self._check_files(file_ids_to_be_created)
                    self._update_file_reference(post_vo.post_id, file_ids_to_be_created)

                if len(file_ids_to_be_deleted) > 0:
                    for file_id in file_ids_to_be_deleted:
                        self.file_mgr.delete_file(file_id)

        return self.post_mgr.update_post_by_vo(params, post_vo)

    @transaction(
        permission="board:Post.write",
        role_types=["SYSTEM_ADMIN", "DOMAIN_ADMIN"],
    )
    @check_required(["post_id"])
    def send(self, params: dict) -> None:
        """Delete post

        Args:
            params (dict): {
                'post_id': 'str',     # required
                'domain_id': 'str'    # injected from auth
            }

        Returns:
            None
        """
        post_id = params["post_id"]
        domain_id = params.get("domain_id")

        post_vo = self.post_mgr.get_post(post_id, domain_id)

        self._check_send_notice_email(post_id, domain_id)

        self.identity_mgr: IdentityManager = self.locator.get_manager(IdentityManager)
        self.config_mgr: ConfigManager = self.locator.get_manager(ConfigManager)

        verified_user_emails_info = {}

        if post_vo.resource_group == "SYSTEM":
            domain_ids = self._get_enabled_state_domain_ids()

            for domain_id in domain_ids:
                language = self._get_language_from_domain_config(domain_id)
                if language not in verified_user_emails_info:
                    verified_user_emails_info[language] = []

                users_emails = self._get_verified_user_emails_from_domain(domain_id)
                verified_user_emails_info[language].extend(users_emails)
        elif post_vo.resource_group == "DOMAIN":
            language = self._get_language_from_domain_config(domain_id)
            if language not in verified_user_emails_info:
                verified_user_emails_info[language] = []

            users_emails = self._get_verified_user_emails_from_domain(domain_id)
            users_emails = list(set(users_emails))
            verified_user_emails_info[language].extend(users_emails)
        else:
            if post_vo.workspaces:
                verified_user_emails = []
                language = self._get_language_from_domain_config(domain_id)
                verified_user_emails_info[language] = []

                enabled_workspaces = (
                    self._get_enabled_state_workspace_ids_from_post_vo_workspaces(
                        domain_id, post_vo.workspaces
                    )
                )
                for workspace_id in enabled_workspaces:
                    users_emails = self._get_verified_user_emails_from_workspace(
                        workspace_id, domain_id
                    )
                    verified_user_emails.extend(users_emails)

                verified_user_emails_info[language].extend(
                    list(set(verified_user_emails))
                )

        total_count = sum(
            [len(emails) for emails in verified_user_emails_info.values()]
        )

        if verified_user_emails_info:
            email_manager = EmailManager()

            _LOGGER.debug(
                f"[send] start to send email to verified user emails (total count = {total_count}"
            )

            for language, verified_user_emails in verified_user_emails_info.items():
                for email in verified_user_emails:
                    email_manager.send_notification_email(
                        email, language, post_vo.contents, post_vo.title
                    )

        _LOGGER.debug(f"[send] verified user email count: {total_count}")

    @transaction(
        permission="board:Post.write",
        role_types=["SYSTEM_ADMIN", "DOMAIN_ADMIN"],
    )
    @check_required(["post_id"])
    def delete(self, params: dict) -> None:
        """Delete post

        Args:
            params (dict): {
                'post_id': 'str',     # required
                'domain_id': 'str'    # injected from auth
            }

        Returns:
            None
        """

        post_id = params["post_id"]
        domain_id = params.get("domain_id")

        post_vo = self.post_mgr.get_post(post_id, domain_id)

        if len(post_vo.files) > 0:
            self.file_mgr: FileManager = self.locator.get_manager(FileManager)

            for file_id in post_vo.files:
                self.file_mgr.delete_file(file_id)

        self.post_mgr.delete_post_vo(post_vo)

    @transaction(
        permission="board:Post.read",
        role_types=[
            "SYSTEM_ADMIN",
            "DOMAIN_ADMIN",
            "WORKSPACE_OWNER",
            "WORKSPACE_MEMBER",
        ],
    )
    @change_value_by_rule("APPEND", "domain_id", "*")
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @check_required(["post_id"])
    def get(self, params: dict) -> Tuple[Post, list]:
        """Get post

        Args:
            params (dict): {
                'post_id': 'str',     # required
                'domain_id': 'str,    # injected from auth
                'workspace_id': 'str' # injected from auth
            }

        Returns:
            post_vo (object)
        """

        post_id = params["post_id"]
        domain_id = params.get("domain_id")
        workspace_id = params.get("workspace_id")

        post_vo = self.post_mgr.get_post(post_id, domain_id, workspace_id)
        self.post_mgr.increase_view_count(post_vo)

        self.file_mgr: FileManager = self.locator.get_manager(FileManager)

        files_info = []
        if len(post_vo.files) > 0:
            files_info = self._get_files_info_from_file_manager(post_vo.files)

        return post_vo, files_info

    @transaction(
        permission="board:Post.read",
        role_types=[
            "SYSTEM_ADMIN",
            "DOMAIN_ADMIN",
            "WORKSPACE_OWNER",
            "WORKSPACE_MEMBER",
        ],
    )
    @change_value_by_rule("APPEND", "domain_id", "*")
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @append_query_filter(
        [
            "board_type",
            "post_id",
            "category",
            "writer",
            "domain_id",
            "workspace_id",
        ]
    )
    def list(self, params: dict) -> dict:
        """List posts

        Args:
            params (dict): {
                'query': 'dict',
                'board_type': 'str',
                'post_id': 'str',
                'category': 'str',
                'writer': 'str',
                'is_pinned': 'bool',
                'is_popup': 'bool',
                'domain_id': 'str',        # injected from auth
                'workspace_id': 'str',     # injected from auth
            }

        Returns:
            posts_vo (object)
            total_count
        """

        query = params.get("query", {})
        return self.post_mgr.list_boards(query)

    @transaction(
        permission="board:Post.read",
        role_types=[
            "SYSTEM_ADMIN",
            "DOMAIN_ADMIN",
            "WORKSPACE_OWNER",
            "WORKSPACE_MEMBER",
        ],
    )
    @change_value_by_rule("APPEND", "domain_id", "*")
    @change_value_by_rule("APPEND", "workspace_id", "*")
    @check_required(["query"])
    @append_query_filter(["domain_id"])
    def stat(self, params: dict) -> dict:
        """List posts

        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',    # required
                'domain_id': 'str',                                        # injected from auth
                'workspace_id': 'str',                                     # injected from auth
            }

        Returns:
            dict: {
                'results': 'list',
                'total_count': 'int'
            }
        """

        query = params.get("query", {})
        return self.post_mgr.stat_boards(query)

    def _check_files(self, file_ids: list) -> None:
        for file_id in file_ids:
            self._verify_file(file_id)

    def _update_file_reference(self, post_id: str, files: list) -> None:
        for file in files:
            reference = {"resource_id": post_id, "resource_type": "board.Post"}
            self.file_mgr.update_file_reference(file, reference)

    def _verify_file(self, file_id: str) -> None:
        file_info = self.file_mgr.get_file(file_id)

        file_state = file_info.get("state")
        if file_state != "DONE":
            raise ERROR_INVALID_FILE_STATE(file_id=file_id, state=file_state)

    def _get_files_info_from_file_manager(self, file_ids: list):
        files_info = []
        for file_id in file_ids:
            file_info = self.file_mgr.get_download_url(file_id)
            files_info.append(file_info)
        return files_info

    def _get_enabled_state_domain_ids(self):
        query_filter = {"filter": [{"k": "state", "v": "ENABLED", "o": "eq"}]}

        domains_info = self.identity_mgr.list_domains({"query": query_filter})
        domain_ids = [domain["domain_id"] for domain in domains_info["results"]]

        return domain_ids

    def _get_verified_user_emails_from_domain(self, domain_id: str) -> list:
        user_emails = []
        query_filter = {
            "only": [
                "user_id",
                "state",
                "email",
                "email_verified",
                "domain_id",
            ],
            "filter": [
                {"k": "domain_id", "v": domain_id, "o": "eq"},
                {"k": "state", "v": "ENABLED", "o": "eq"},
                {"k": "email_verified", "v": True, "o": "eq"},
            ],
        }
        response = self.identity_mgr.list_users(domain_id, {"query": query_filter})
        users_info = response.get("results", [])
        total_count = response.get("total_count", 0)
        user_emails.extend([user["email"] for user in users_info])

        _LOGGER.debug(
            f"[_get_verified_user_emails_from_domain] user email count: {total_count} in domain_id: {domain_id}"
        )

        return user_emails

    def _get_enabled_state_workspace_ids_from_post_vo_workspaces(
        self, domain_id: str, workspace_ids: list
    ) -> list:
        enabled_workspaces_in_domain_set = set(
            self._get_enabled_state_workspaces(domain_id)
        )
        workspace_ids_set = set(workspace_ids)
        common_workspace_ids = enabled_workspaces_in_domain_set & workspace_ids_set
        return list(common_workspace_ids)

    def _get_enabled_state_workspaces(self, domain_id: str) -> list:
        workspace_ids = []
        query_filter = {
            "filter": [
                {"k": "domain_id", "v": domain_id, "o": "eq"},
                {"k": "state", "v": "ENABLED", "o": "eq"},
            ]
        }

        workspaces_info = self.identity_mgr.list_workspaces(
            {"query": query_filter}, domain_id
        )
        workspace_ids.extend(
            [
                workspace_info["workspace_id"]
                for workspace_info in workspaces_info["results"]
            ]
        )

        return workspace_ids

    def _get_verified_user_emails_from_workspace(
        self, workspace_id: str, domain_id: str
    ) -> list:
        workspace_user_emails = []
        query_filter = {
            "filter": [
                {"k": "state", "v": "ENABLED", "o": "eq"},
                {"k": "domain_id", "v": domain_id, "o": "eq"},
                {"k": "email_verified", "v": True, "o": "eq"},
            ],
        }
        response = self.identity_mgr.list_workspace_users(
            {"query": query_filter, "workspace_id": workspace_id},
            domain_id,
            workspace_id,
        )
        users_info = response.get("results", [])
        total_count = response.get("total_count", 0)
        workspace_user_emails.extend([user["email"] for user in users_info])

        _LOGGER.debug(
            f"[_get_verified_user_emails_from_workspace] user email count: {total_count} in workspace_id: {workspace_id}"
        )

        return workspace_user_emails

    def _get_language_from_domain_config(self, domain_id: str) -> str:
        language = "en"
        try:
            domain_config_info = self.config_mgr.get_domain_config(domain_id)
            domain_config_data = domain_config_info.get("data", {})
            language = domain_config_data.get("language", "en")
        except Exception:
            _LOGGER.debug(
                f"[_get_language_from_domain_config] {domain_id} domain config not found."
            )

        return language

    @staticmethod
    def _check_send_notice_email(post_id: str, domain_id: str) -> None:
        if cache.is_set():
            cached_send_notice_email_info = cache.get(
                f"board:post:send:{post_id}:{domain_id}"
            )
            if cached_send_notice_email_info:
                raise ERROR_NOTICE_EMAIL_ALREADY_SENT(post_id=post_id)
            else:
                email_send_retry_interval = config.get_global(
                    "EMAIL_SEND_RETRY_INTERVAL", 180
                )
                cache.set(
                    f"board:post:send:{post_id}:{domain_id}",
                    True,
                    expire=email_send_retry_interval,
                )

    @staticmethod
    def _valid_options(options: dict) -> None:
        supported_options_key = ["is_pinned", "is_popup"]

        for key in options.keys():
            if key not in supported_options_key:
                raise ERROR_INVALID_KEY_IN_OPTIONS(key=key)
