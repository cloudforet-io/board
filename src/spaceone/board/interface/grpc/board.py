from spaceone.api.board.v1 import board_pb2, board_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Board(BaseAPI, board_pb2_grpc.BoardServicer):

    pb2 = board_pb2
    pb2_grpc = board_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            return self.locator.get_info('BoardInfo', board_service.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            return self.locator.get_info('BoardInfo', board_service.update(params))

    def set_categories(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            return self.locator.get_info('BoardInfo', board_service.set_categories(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            board_service.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            return self.locator.get_info('BoardInfo', board_service.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            board_vos, total_count = board_service.list(params)
            return self.locator.get_info('BoardsInfo',
                                         board_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('BoardService', metadata) as board_service:
            return self.locator.get_info('BoardInfo', board_service.stat(params))
