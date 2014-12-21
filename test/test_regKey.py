from unittest import TestCase
from windows.registry import RegKey
import winreg

class TestRegKey(TestCase):
    def test_valid_init(self):
        r = RegKey(winreg.HKEY_CLASSES_ROOT, "*")
        self.assertIsNotNone(r, "Couldn't create RegKey")

    def test_bad_hive(self):
        self.assertRaises(OSError, RegKey, 10, "Software")

    def test_bad_key(self):
        self.assertRaises(OSError, RegKey, winreg.HKEY_LOCAL_MACHINE, "Foo")
