import logging

from spaceone.core import cache
from spaceone.core.manager import BaseManager
from spaceone.core.connector.space_connector import SpaceConnector


_LOGGER = logging.getLogger(__name__)


class FileManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_manager_connector: SpaceConnector = self.locator.get_connector('SpaceConnector',
                                                                                 service='file_manager')

    def get_file(self, file_id, domain_id):
        return self.file_manager_connector.dispatch('File.get', {'file_id': file_id, 'domain_id': domain_id})

    def update_file_reference(self, file_id, reference, domain_id):
        return self.file_manager_connector.dispatch('File.update', {'file_id': file_id, 'reference': reference,
                                                                    'domain_id': domain_id})

    def delete_file(self, file_id, domain_id):
        return self.file_manager_connector.dispatch('File.delete', {'file_id': file_id, 'domain_id': domain_id})

    @cache.cacheable(key='board:file-download-url:{domain_id}:{file_id}', expire=600)
    def get_download_url(self, file_id, domain_id):
        return self.file_manager_connector.dispatch('File.get_download_url',
                                                    {'file_id': file_id, 'domain_id': domain_id})
