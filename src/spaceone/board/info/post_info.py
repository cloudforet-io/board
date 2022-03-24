import functools

from spaceone.api.board.v1 import post_pb2
from spaceone.core import utils

from spaceone.board.model.post_model import Post, PostOptions

__all__ = ['PostInfo', 'PostsInfo']


def PostOptionsInfo(vo: PostOptions):
    if vo is None:
        return None
    else:
        info = {
            'is_pinned': vo.is_pinned,
            'is_popup': vo.is_popup
        }
        return post_pb2.PostOptions(**info)


def PostInfo(post_vo: Post, minimal=False):
    info = {
        'board_id': post_vo.board_id,
        'post_id': post_vo.post_id,
        'category': post_vo.category,
        'title': post_vo.title,
        'contents': post_vo.contents,
        'view_count': post_vo.view_count,
        'writer': post_vo.writer,
        'scope': post_vo.scope
    }

    if not minimal:
        info.update({
            'options': PostOptionsInfo(post_vo.options),
            'domain_id': post_vo.domain_id,
            'user_id': post_vo.user_id,
            'created_at': utils.datetime_to_iso8601(post_vo.created_at),
            'updated_at': utils.datetime_to_iso8601(post_vo.updated_at)
        })

    return post_pb2.PostInfo(**info)


def PostsInfo(post_vos, total_count, **kwargs):
    return post_pb2.PostsInfo(results=list(
        map(functools.partial(PostInfo, **kwargs), post_vos)), total_count=total_count)
