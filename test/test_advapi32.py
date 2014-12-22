from unittest import TestCase
from winapi.advapi32 import Advapi32, TokenPrivileges, SecurityInformation
import os.path


class TestAdvapi32(TestCase):
    def test_CreateWellKnownSid(self):
        self.assertIsNotNone(Advapi32.CreateWellKnownSid(22))

    def test_CreateWellKnownSid_fails(self):
        try:
            Advapi32.CreateWellKnownSid(0xff)
        except OSError as e:
            self.assertEqual(e.winerror, 87)

    def test_LookupAccountSidW(self):
        # TODO What is the binary sid of the group?
        sid = Advapi32.CreateWellKnownSid(22)
        self.assertIsNotNone(sid)

        name, domain, snu = Advapi32.LookupAccountSidW(sid=sid)
        self.assertEqual(name, "SYSTEM")
        self.assertEqual(domain, "NT AUTHORITY")
        self.assertEqual(snu, 5)

    def test_LookupAccountSidW_fails(self):
        self.assertRaises(OSError, Advapi32.LookupAccountSidW, sid="foo")

    def test_GetFileSecurityW(self):
        f = "C:\\Windows\\system32\\ntdll.dll"
        self.failIf(not os.path.exists(f))
        sd = Advapi32.GetFileSecurityW(f,
                                       SecurityInformation.OWNER_SECURITY_INFORMATION |
                                       SecurityInformation.GROUP_SECURITY_INFORMATION |
                                       SecurityInformation.DACL_SECURITY_INFORMATION)
        self.assertIsNotNone(sd)

    def test_OpenProcessToken(self):
        import ctypes
        hProc = ctypes.windll.kernel32.GetCurrentProcess()
        self.assertEqual(hProc, -1)
        hToken = Advapi32.OpenProcessToken(hProc, TokenPrivileges.TOKEN_QUERY)
        self.assertIsNot(0, hToken, msg="Failed to call OpenProcessToken properly")