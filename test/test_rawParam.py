from unittest import TestCase
from ctypeshelper.ctypeshelper import RawParam
from ctypes import c_ulong, c_uint


class TestRawParam(TestCase):
    def setUp(self):
        self.raw = RawParam("foo", 0x1, c_ulong, lambda: "foo", True)

    def test_flags(self):
        self.assertEqual(self.raw.flags, 0x1)
        self.assertRaises(Exception, setattr, self.raw, "flags", 2)

    def test_param_type(self):
        self.assertEqual(self.raw.param_type, c_ulong)
        self.assertRaises(Exception, setattr, self.raw, "param_type", c_uint)

    def test_name(self):
        self.assertEqual(self.raw.name, "foo")
        self.assertRaises(Exception, setattr, self.raw, "name", "bar")

    def test_should_return(self):
        self.assertEqual(self.raw.should_return, True)
        self.assertRaises(Exception, setattr, self.raw, "should_return", False)

    def test_resolve(self):
        self.assertEqual(self.raw.resolve("foo"), "foo")

    def test_has_generator(self):
        self.assertTrue(self.raw.has_generator)

    def test_generate(self):
        self.assertEqual(self.raw.generate(), "foo")

