from ctypes import *
from maya.ctypeshelper import resolve


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
    from maya.winapi.advapi32 import Advapi32

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
    from maya.winapi.advapi32 import Advapi32, TokenPrivileges
    hProc = ctypes.windll.kernel32.GetCurrentProcess()
    print(hProc)

    hToken = Advapi32.OpenProcessToken(hProc, TokenPrivileges.TOKEN_QUERY)
    print(hToken)


def test3():
    from maya.winapi.kernel32 import Kernel32, Toolhelp32Flags as th

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
    from maya.winapi.advapi32 import Advapi32, TokenPrivileges, TokenInformationClass
    hProc = ctypes.windll.kernel32.GetCurrentProcess()
    print(hProc)    # Will be -1
    hToken = Advapi32.OpenProcessToken(hProc, TokenPrivileges.TOKEN_QUERY)
    print(hToken)
    info = Advapi32.GetTokenInformation(hToken, TokenInformationClass.TokenUser)
    print(info)


def test5():
    x = TestStructure()
    x.switch = 4
    x.field.four.switch = 3
    x.field.four.field.three = 42
    y = resolve(x)
    print("Frag" + str(y))


def test6():
    from maya.winutils.osinfo import whoami, get_effective_token

    print(whoami())
    token = get_effective_token()
    print(token)
    for priv in token.privileges:
        print("Enabling {0}".format(priv.name))
        token.enable_privilege(priv)

    #for proc in find_user_processes("SYSTEM"):
    #    print(proc)
    #    try:
    #        token = proc.get_token()
    #        print(token.user)
    #        for p in token.privileges:
    #            print(p)
    #    except PermissionError:
    #        print("Couldn't open {0}".format(proc.pid))
    #    print("")


def test7():
    from maya.ctypeshelper import AutoStructure

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
    d = {'Int': 1, 'Byte': 2}
    struct = TestStructure()
    print(struct.MyStruct)
    struct.MyStruct = d
    print(struct.MyStruct)

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)

    # test1()
    # test2()
    test3()
    # test4()
    test5()
    # test6()
    test7()