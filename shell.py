from ctypes import *
import logging
from ctypeshelper import resolve


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
        ("two", c_ubyte),
        ("three", c_size_t),
        ("four", TestSubStructure)
    ]


class TestStructure(Structure):
    _map_ = {
        "field": lambda x: x.switch
    }
    _fields_ = [
        ("switch", c_ulong),
        ("field", TestUnion)
    ]


def errcheck(result, func, args):
    print(result)
    return args


def test1():
    from winapi.advapi32 import Advapi32

    try:
        sid = Advapi32.CreateWellKnownSid(0xff)
    except OSError as e:
        print(e.winerror)
        print(dir(e))

    sid = Advapi32.CreateWellKnownSid(22)
    print(sid)

    # print("foo")
    string_sid = Advapi32.ConvertSidToStringSidW(sid)
    print(string_sid)

    name, domain, snu = Advapi32.LookupAccountSidW(sid)
    print(name, domain, snu)


def test2():
    import ctypes
    from winapi.advapi32 import Advapi32, TokenPrivileges
    hProc = ctypes.windll.kernel32.GetCurrentProcess()
    print(hProc)

    hToken = Advapi32.OpenProcessToken(hProc, TokenPrivileges.TOKEN_QUERY)
    print(hToken)


def test3():
    from winapi.kernel32 import Kernel32, Toolhelp32Flags as th

    hSnapshot = Kernel32.CreateToolhelp32Snapshot(th.TH32CS_SNAPALL)
    proc = Kernel32.Process32First(hSnapshot)
    print(proc)
    while True:
        try:
            proc = Kernel32.Process32Next(hSnapshot)
            print(proc)
        except OSError:
            break


def test4():
    import ctypes
    from winapi.advapi32 import Advapi32, TokenPrivileges, TOKEN_INFORMATION_CLASS
    hProc = ctypes.windll.kernel32.GetCurrentProcess()
    print(hProc)    # Will be -1
    hToken = Advapi32.OpenProcessToken(hProc, TokenPrivileges.TOKEN_QUERY)
    print(hToken)
    info = Advapi32.GetTokenInformation(hToken, TOKEN_INFORMATION_CLASS.TokenUser)
    print(info)


def test5():
    x = TestStructure()
    x.switch = 4
    x.field.four.switch = 3
    x.field.four.field.three = 42
    y = resolve(x, {})
    print("Frag" + str(y))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from ctypeshelper import InParam

    # test1()
    # test2()
    # test3()
    #test4()
    test5()
