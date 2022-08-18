import functools

from spaceone.api.board.v1 import board_pb2
from spaceone.core.pygrpc.message_type import change_struct_type
from spaceone.board.model.board_model import Board
from spaceone.core import utils


def BoardInfo(board_vo: Board, minimal=False):
    info = {
        'board_id': board_vo.board_id,
        'name': board_vo.name,
        'categories': board_vo.categories,
    }

    if not minimal:
        info.update({
            'tags': change_struct_type(board_vo.tags),
            'created_at': utils.datetime_to_iso8601(board_vo.created_at)
        })

    return board_pb2.BoardInfo(**info)


def BoardsInfo(board_vos, total_count, **kwargs):
    return board_pb2.BoardsInfo(results=list(
        map(functools.partial(BoardInfo, **kwargs), board_vos)), total_count=total_count)
