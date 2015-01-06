from unittest import TestCase
from maya.ctypeshelper import AutoStructure
from ctypes import *


class SubStructure(AutoStructure):
    _fields_ = [
        ("Int", c_uint),
        ("Byte", c_ubyte)
    ]

class TestStructure(AutoStructure):
    _fields_ = [
        ("Basic", c_ulong),
        ("Array", c_ubyte * 8),
        ("MyStruct", SubStructure)
    ]


class TestAutoStructure(TestCase):
    def setUp(self):
        self.struct = TestStructure()

    #def test_set_number(self):
    #    self.struct.Basic = 3

    #def test_set_array(self):
    #    array = [1, 2, 3, 4, 5, 6, 7, 8]
    #    self.struct.Array = array
    #    y = self.struct.Array
    #    self.assertTrue(all(map(lambda x: x[0] == x[1], zip(self.struct.Array, array))))

    #def test_set_byte_string(self):
    #    s = bytes("abcd1234", "utf-8")
    #    self.fail()

    #def test_set_structure(self):
    #    d = {'Int': 1, 'Byte': 2}
    #    self.assertEqual(self.struct.MyStruct.Int, 0)
    #    self.struct.MyStruct = d
    #    self.assertEqual(self.struct.MyStruct.Int, 1)
    #    self.assertEqual(self.struct.MyStruct.Byte, 2)
    #    self.struct.MyStruct.Int = 3
    #    self.assertEqual(self.struct.MyStruct.Int, 3)

