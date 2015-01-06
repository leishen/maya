from unittest import TestCase
from ctypes import *
from maya.ctypeshelper import dict2struct


class SubStructure(Structure):
    _fields_ = [
        ("one", c_ulong),
        ("two", c_ulong)
    ]


class TestStructure(Structure):
    _fields_ = [
        ("num", c_ulong),
        ("array", c_ubyte * 8),
        ("struct", SubStructure)
    ]


class TestDict2struct(TestCase):
    def test_dict2struct(self):
        arr = [1, 2, 3, 4, 5, 6, 7, 8]
        d = {
            'num': 1,
            'array' : arr,
            'struct' : {
                'one': 1,
                'two': 2
            }
        }
        y = dict2struct(d, TestStructure)
        self.assertEqual(y.num, 1)
        self.assertTrue(all(map(lambda x: x[0] == x[1], zip(arr, y.array))))
        self.assertEqual(y.struct.one, 1)
