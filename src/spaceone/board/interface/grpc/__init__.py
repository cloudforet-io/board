from spaceone.core.pygrpc.server import GRPCServer
from spaceone.board.interface.grpc.board import Board
from spaceone.board.interface.grpc.post import Post

_all_ = ["app"]

app = GRPCServer()
app.add_service(Board)
app.add_service(Post)
