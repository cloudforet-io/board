import functools

from spaceone.api.board.v1 import post_pb2
from spaceone.core.pygrpc.message_type import change_struct_type, change_list_value_type
from spaceone.core import utils

from spaceone.board.model.post_model import Post

__all__ = ['PostInfo', 'PostsInfo']


def PostInfo(post_vo: Post, minimal=False, files_info=None):
    info = {
        'board_id': post_vo.board_id,
        'post_id': post_vo.post_id,
        'post_type': post_vo.post_type,
        'category': post_vo.category,
        'title': post_vo.title,
        'scope': post_vo.scope,
        'domain_id': post_vo.domain_id,
    }

    if not minimal:
        info.update({
            'contents': post_vo.contents,
            'view_count': post_vo.view_count,
            'writer': post_vo.writer,
            'options': change_struct_type(post_vo.options),
            'user_id': post_vo.user_id,
            'user_domain_id': post_vo.user_domain_id,
            'created_at': utils.datetime_to_iso8601(post_vo.created_at),
            'updated_at': utils.datetime_to_iso8601(post_vo.updated_at)
        })

        if files_info:
            info['files'] = change_list_value_type(files_info)
        else:
            info['files'] = change_list_value_type(post_vo.files)

    return post_pb2.PostInfo(**info)


def PostsInfo(post_vos, total_count, **kwargs):
    return post_pb2.PostsInfo(results=list(
        map(functools.partial(PostInfo, **kwargs), post_vos)), total_count=total_count)
