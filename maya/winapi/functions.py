from ctypes import WINFUNCTYPE, WinError, HRESULT
from ctypes.wintypes import BOOL, HANDLE
from maya.ctypeshelper import HelperFunc
from functools import wraps
import logging


__all__ = ['WinFunc', 'HresultWinFunc', 'WinapiWinFunc', 'BoolWinFunc']


def trace(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        logging.debug("{0}({1}{2})".format(fn.__name__, args, kwargs))
        return fn(*args, **kwargs)
    return inner


class WinFunc(HelperFunc):
    def __init__(self, name, module, ret, double=False):
        # Double indicates whether the function returns allocation size information
        # on the first call
        super().__init__(WINFUNCTYPE, name, module, ret)


class HresultWinFunc(WinFunc):
    def __init__(self, name, module):
        super().__init__(name, module, HRESULT)

    @staticmethod
    def errcheck(result, func, args):
        if 0 != result:
            raise WinError()
        return WinFunc.errcheck(result, func, args)


class WinapiWinFunc(WinFunc):
    def __init__(self, name, module):
        super().__init__(name, module, HRESULT)

    @staticmethod
    def errcheck(result, func, args):
        if 0 != result:
            raise WinError()
        return WinFunc.errcheck(result, func, args)


class BoolWinFunc(WinFunc):
    def __init__(self, name, module):
        super().__init__(name, module, BOOL)

    @staticmethod
    def errcheck(result, func, args):
        if 0 == result:
            raise WinError()
        return WinFunc.errcheck(result, func, args)


class HandleWinFunc(WinFunc):
    def __init__(self, name, module):
        super().__init__(name, module, HANDLE)

    @staticmethod
    def errcheck(result, func, args):
        if result == -1 or not result:
            raise WinError()
        return result