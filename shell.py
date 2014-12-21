

def errcheck(result, func, args):
    print(result)
    return args


def test1():
    from windows.security import (CreateWellKnownSid,
                                  ConvertSidToStringSidW,
                                  LookupAccountSidW,
                                  GetFileSecurityW,
                                  OWNER_SECURITY_INFORMATION,
                                  GROUP_SECURITY_INFORMATION,
                                  DACL_SECURITY_INFORMATION,
                                  SACL_SECURITY_INFORMATION)

    sid = CreateWellKnownSid(22)
    print(sid)
    # print("foo")
    stringsid = ConvertSidToStringSidW(sid)
    print(stringsid)

    name, domain, snu = LookupAccountSidW(sid=sid)
    print(name, domain, snu)


    sd = GetFileSecurityW("C:\\Windows\\system32\\ntdll.dll",
                          OWNER_SECURITY_INFORMATION | GROUP_SECURITY_INFORMATION |
                          DACL_SECURITY_INFORMATION| SACL_SECURITY_INFORMATION)
    print(sd)

def test2():
    from ctypeshelper.ctypeshelper import HelperFunc, InParam, InOutParam, ReturnOutParam
    import ctypes
    from ctypes import c_ubyte, POINTER, c_void_p, pointer, WINFUNCTYPE
    from ctypes.wintypes import LPWSTR, DWORD, LPDWORD, BOOL
    advapi32 = ctypes.windll.advapi32

    SECURITY_MAX_SID_SIZE = 68
    PLPWSTR = POINTER(LPWSTR)
    SID = c_ubyte * SECURITY_MAX_SID_SIZE
    PSID = POINTER(SID)

    CreateWellKnownSid = HelperFunc(WINFUNCTYPE, "CreateWellKnownSid", advapi32, BOOL)
    CreateWellKnownSid.params = [
        InParam(DWORD, "WellKnownSidType", None),
        InParam(c_void_p, "DomainSid", lambda: c_void_p(0)),
        ReturnOutParam(PSID, "pSid", lambda: pointer(SID(0))),
        InOutParam(LPDWORD, "cbSid", lambda: pointer(DWORD(SECURITY_MAX_SID_SIZE)))
    ]

    sid = CreateWellKnownSid(22)
    print(sid)



if __name__ == "__main__":
    test1()
