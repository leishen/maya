from unittest import TestCase
from ctypes import *
# from ctypeshelper import resolve
import logging

def struct2dict(cval):
    if not isinstance(cval, Structure):
        raise ValueError("Must be a structure")
    d = {}
    if hasattr(cval, '_unions_'):
        d['_unions_'] = cval._unions_
    for name, typ in cval._fields_:
        d[name] = getattr(cval, name)
    return d


def resolve(cval):
    logging.debug("resolve {0}".format(cval))

    def resolve_union(cval, switch):
        logging.debug(switch)
        if hasattr(cval.__class__, "_map_"):
            which = cval._map_[switch]
            return resolve(getattr(cval, which))
        else:
            return cval

    if hasattr(cval, "value"):             # basic type
        logging.debug("value: {0}".format(cval.value))
        return cval.value
    elif hasattr(cval, "contents"):        # pointer type
        logging.debug("contents: {0}".format(cval.contents))
        ret = resolve(cval.contents)
        return ret
    elif isinstance(cval, Array):
        logging.debug("Byte array")
        return bytes(cval[:])
    elif isinstance(cval, dict) or isinstance(cval, Structure):
        # If it's a dict, we got this from an errcheck call using parameters instead of a structure
        if isinstance(cval, Structure):
            # Map structure to dict just to ease maintenance
            cval = struct2dict(cval)
        f = {}
        for name, value in cval.items():
            if name == '_unions_':
                continue
            if isinstance(value, Union):
                if '_unions_' in cval:
                    f[cval['_unions_'][name]] = resolve(cval[cval['_unions_'][name]])
                    f[name] = resolve_union(cval[name], f[cval['_unions_'][name]])
                else:
                    f[name] = cval[name]
            else:
                f[name] = resolve(cval[name])
        return f
    else:
        return cval

class TestSubUnion(Union):
    _map_ = {
        1: "one",
        2: "two",
        3: "three",
        4: "four"
    }

    _fields_ = [
        ("one", c_ulong),
        ("two", c_byte),
        ("three", c_size_t),
        ("four", c_short)
    ]


class TestSubStructure(Structure):
    _anonymous = ("field",)
    _unions_ = {"field": "switch"}
    _fields_ = [
        ("switch", c_ulong),
        ("field", TestSubUnion)
    ]


class TestUnion(Union):
    _map_ = {
        1: "one",
        2: "two",
        3: "three",
        4: "four"
    }

    _fields_ = [
        ("one", c_ulong),
        ("two", c_byte),
        ("three", c_size_t),
        ("four", TestSubStructure)
    ]


class TestStructure(Structure):
    _unions_ = {
        "field": "switch"
    }
    _fields_ = [
        ("switch", c_ulong),
        ("field", TestUnion)
    ]


class TestResolve_value(TestCase):
    def setUp(self):
        # Create the structure
        pass

    def test_resolve_value_structure(self):
        x = TestStructure()
        x.switch = 4
        x.field.four.switch = 3
        x.field.four.field.three = 42
        y = resolve(x)
        logging.debug(y)
        self.assertEqual(y['field']['field'], 42)

    def test_resolve_parameters(self):
        # Create a bunch of parameters
        # Create a dict of {name: cval} for all parameters
        # If there's a union, add the _unions_ field to the dict
        # Resolve it!
        self.fail()