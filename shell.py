

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


def test6():
    from maya.winutils.osinfo import whoami, get_effective_token, TokenPrivileges

    print(whoami())
    token = get_effective_token(access=TokenPrivileges.TOKEN_QUERY | TokenPrivileges.TOKEN_ADJUST_PRIVILEGES)
    print(token)
    for priv in token.privileges:
        print("Enabling {0}".format(priv.name))
        token.enable_privilege(priv)
    print(list(token.privileges))


def test7():
    from maya.winutils.osinfo import Snapshot
    with Snapshot() as snap:
        for proc in snap.processes:
            print(proc)
            try:
                for mod in proc.modules:
                    print("    {0}".format(mod))
            except:
                pass


def test8():
    from maya.winutils.osinfo import whoami, find_user_processes
    user = whoami()
    print(user)
    for proc in find_user_processes("Greg"):
        print(proc)


if __name__ == "__main__":
    # test1()
    # test2()
    # test3()
    # test4()
    # test6()
    # test7()
    test8()
