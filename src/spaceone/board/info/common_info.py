from spaceone.core.pygrpc.message_type import *

__all__ = ['StatisticsInfo']


def StatisticsInfo(result):
    return change_struct_type(result)
