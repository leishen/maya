from ctypes import WINFUNCTYPE, WinError, HRESULT
from ctypes.wintypes import BOOL, HANDLE
from ctypeshelper import HelperFunc


__all__ = ['WinFunc', 'HresultWinFunc', 'WinapiWinFunc', 'BoolWinFunc']


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
        if result == -1:
            raise WinError()
        return args