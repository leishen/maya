

def errcheck(result, func, args):
    print(result)
    return args


def test1():
    from winapi import Advapi32

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

    name, domain, snu = Advapi32.LookupAccountSidW(sid=sid)
    print(name, domain, snu)


def test2():
    import ctypes
    from winapi import Advapi32, TOKEN_QUERY
    hProc = ctypes.windll.kernel32.GetCurrentProcess()
    print(hProc)

    hToken = Advapi32.OpenProcessToken(hProc, TOKEN_QUERY)
    print(hToken)


if __name__ == "__main__":
    from ctypeshelper import InParam

    # test1()
    test2()