

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


if __name__ == "__main__":
    from examples.registry import registry_example
    registry_example()