import logging

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector

_LOGGER = logging.getLogger(__name__)


class FileManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_manager_connector: SpaceConnector = self.locator.get_connector(
            SpaceConnector, service="file_manager"
        )

    def get_file(self, file_id: str) -> dict:
        return self.file_manager_connector.dispatch("File.get", {"file_id": file_id})

    def update_file_reference(self, file_id: str, reference: dict) -> dict:
        return self.file_manager_connector.dispatch(
            "File.update",
            {"file_id": file_id, "reference": reference},
        )

    def delete_file(self, file_id: str) -> None:
        return self.file_manager_connector.dispatch("File.delete", {"file_id": file_id})

    @cache.cacheable(key="board:file-download-url:{file_id}", expire=600)
    def get_download_url(self, file_id: str) -> dict:
        return self.file_manager_connector.dispatch(
            "File.get_download_url", {"file_id": file_id}
        )
