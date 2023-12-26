import copy
import logging
from typing import Tuple, Union

from spaceone.core.service import *
from spaceone.board.error import *

from spaceone.board.manager.post_manager import PostManager
from spaceone.board.manager.file_manager import FileManager
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

    @transaction(
        permission="board:Post.write",
        role_types=["SYSTEM_ADMIN", "DOMAIN_ADMIN"],
    )
    @check_required(["board_type", "title", "contents"])
    def create(self, params: dict) -> Post:
        """Create post

        Args:
            params (dict): {
                'board_type': 'str',       # required
                'category': 'str',
                'title': 'str',            # required
                'contents': 'str',         # required
                'files' : 'list',
                'options': 'dict',
                'writer': 'str',
                'resource_group': 'str',   # required
                'domain_id': 'str',        # injected from auth
                'user_id': 'str'           # injected from auth
            }

        Returns:
            post_vo (object)
        """
        resource_group = params["resource_group"]
        if resource_group == "SYSTEM":
            params["domain_id"] = "*"

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
                'post_id': 'str',    # required
                'category': 'str',
                'title': 'str',
                'contents': 'str',
                'files' : 'list',
                'options': 'dict',
                'writer': 'str',
                'domain_id': 'str',        # injected from auth
                'user_id': 'str'           # injected from auth
            }

        Returns:
            post_vo (object)
        """
        post_id = params["post_id"]
        domain_id = params.get("domain_id")

        post_vo = self.post_mgr.get_post(post_id, domain_id)

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
    def send_notification(self, params: dict) -> None:
        """Delete post

        Args:
            params (dict): {
                'post_id': 'str',     # required
                'domain_id': 'str'    # injected from auth
                'user_id': 'str'      # injected from auth
            }

        Returns:
            None
        """
        pass

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
                'user_id': 'str'      # injected from auth
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
    @check_required(["post_id"])
    def get(self, params: dict) -> Tuple[Post, list]:
        """Get post

        Args:
            params (dict): {
                'post_id': 'str',     # required
                'domain_id': 'str,    # injected from auth
                'user_id': 'str'      # injected from auth
            }

        Returns:
            post_vo (object)
        """

        post_id = params["post_id"]
        domain_id = params.get("domain_id")

        post_vo = self.post_mgr.get_post(post_id, domain_id)
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
    @append_query_filter(
        [
            "board_type",
            "post_id",
            "category",
            "writer",
            "domain_id"
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
                'user_projects': 'list'    # injected from auth
                'user_id': 'str'           # injected from auth
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
    @check_required(["query"])
    @append_query_filter(["domain_id"])
    def stat(self, params: dict) -> dict:
        """List posts

        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',    # required
                'domain_id': 'str',                                        # injected from auth
                'workspace_id': 'str',                                     # injected from auth
                'user_projects': 'list'                                    # injected from auth
                'user_id': 'str'                                           # injected from auth
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

    @staticmethod
    def _valid_options(options: dict) -> None:
        exact_keys = ["is_pinned", "is_popup"]

        for key in options:
            if key not in exact_keys:
                raise ERROR_INVALID_KEY_IN_OPTIONS
