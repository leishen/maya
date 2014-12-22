"""Ctypeshelper is an implementation meant to make creating native function calls
using ctypes easier.  It contains markup for specifying the function, its parameters,
default functions to generate new parameter when functions are called, and logic to
specify which parameters are returned and which are ignored on return.
"""

from .ctypeshelper import *

__all__ = ['RawParam', 'ResolvedParam', 'InParam', 'ReturnInParam', 'OutParam', 'ReturnOutParam', 'InOutParam',
           'ReturnInOutParam', 'HelperFunc']
