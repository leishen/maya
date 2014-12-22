#!/usr/bin/env python3
import winreg
from collections import namedtuple

__all__ = ['Key', 'Value', 'RegKey']

Key = namedtuple('Key', 'subkeys', 'values', 'modified')
Value = namedtuple('Value', 'name', 'type', 'data')


class RegKey:
    def __init__(self, hive, key):
        self._hive = winreg.ConnectRegistry(None, hive)
        self._hkey = winreg.OpenKey(self._hive, key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        winreg.CloseKey(self._handle)
        winreg.CloseKey(self._hive)
        # Pass any error along to the application
        return False

    def _iter_keys(self):
        i = 0
        done = False
        while not done:
            try:
                key = winreg.EnumKey(self._hkey, i)
                hkey = winreg.OpenKey(self._hkey, key, access=winreg.KEY_READ)
                cKeys, cValues, lastmod = winreg.QueryInfoKey(hkey)
                yield Key(cKeys, cValues, lastmod)
            except OSError:
                done = True

    def _iter_values(self):
        i = 0
        done = False
        while not done:
            try:
                name, data, typ = winreg.EnumValue(self._hkey, i)
                yield Value(name, typ, data)
            except OSError:
                done = True

    def __iter__(self):
        for k in self._iter_keys():
            yield k
        for v in self._iter_values():
            yield v

    def dump(self):
        pass

