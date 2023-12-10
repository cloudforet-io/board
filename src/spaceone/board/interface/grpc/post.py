from spaceone.api.board.v1 import post_pb2, post_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Post(BaseAPI, post_pb2_grpc.PostServicer):

    pb2 = post_pb2
    pb2_grpc = post_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PostService', metadata) as post_service:
            return self.locator.get_info('PostInfo', post_service.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PostService', metadata) as post_service:
            return self.locator.get_info('PostInfo', post_service.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PostService', metadata) as post_service:
            post_service.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PostService', metadata) as post_service:
            post_vo, files_info = post_service.get(params)
            return self.locator.get_info('PostInfo', post_vo, files_info=files_info)

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PostService', metadata) as post_service:
            post_vos, total_count = post_service.list(params)
            return self.locator.get_info('PostsInfo',
                                         post_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('PostService', metadata) as post_service:
            return self.locator.get_info('PostInfo', post_service.stat(params))
