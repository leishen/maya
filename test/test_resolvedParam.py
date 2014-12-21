from unittest import TestCase
from ctypes import *
from ctypeshelper import ResolvedParam


class TestResolvedParam(TestCase):
    def test_resolve_Array_type(self):
        param = ResolvedParam("foo", 2, c_char_p, None, False)
        typ = c_ubyte * 1024
        x = typ(0)
        self.assertIsInstance(param.resolve(x), bytes)

    def test_resolve_basic_type(self):
        x = c_ulong(42)
        param = ResolvedParam("foo", 1, c_ulong, None, False)
        self.assertIsInstance(param.resolve(x), int)
        self.assertEqual(param.resolve(x), 42)

    def test_resolve_pointer_type(self):
        x = pointer(c_ulong(54))
        param = ResolvedParam("foo", 2, POINTER(c_ulong), None, False)
        self.assertIsInstance(param.resolve(x), int)
        self.assertEqual(param.resolve(x), 54)

    # def test_resolve_type_safety(self):
    #     x = c_ulong(42)
    #     param = ResolvedParam("foo", 1, c_char_p, None, False)
    #     param.resolve(x)
    #     self.assertRaises(Exception, param.resolve, x)
