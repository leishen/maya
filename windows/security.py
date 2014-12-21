#!/usr/bin/env python3

from ctypes import *
from ctypes.wintypes import *
from ctypeshelper.ctypeshelper import *
from ctypeshelper.windows import *


advapi32 = ctypes.windll.advapi32

# Constants
SECURITY_MAX_SID_SIZE = 68

# Types
SID = c_ubyte * SECURITY_MAX_SID_SIZE
PSID = POINTER(SID)


#
# Functions
#

# First param must be c_void_p to be received from output of SID producing functions
# as a bytes string and marshaled properly when passed to other functions
ConvertSidToStringSidW = BoolWinFunc("ConvertSidToStringSidW", advapi32)
ConvertSidToStringSidW.params = [
    InParam(c_void_p, "sid", None),
    ReturnOutParam(POINTER(LPWSTR), "string_sid", lambda: pointer(c_wchar_p(0)))
]


WinNullSid = 0

CreateWellKnownSid = BoolWinFunc("CreateWellKnownSid", advapi32)
CreateWellKnownSid.params = [
    InParam(DWORD, "WellKnownSidType"),
    InParam(c_void_p, "DomainSid", lambda: c_void_p(0)),
    ReturnOutParam(PSID, "pSid", lambda: pointer(SID(0))),
    InOutParam(LPDWORD, "cbSid", lambda: pointer(DWORD(SECURITY_MAX_SID_SIZE)))
]

OWNER_SECURITY_INFORMATION = 0x00000001
GROUP_SECURITY_INFORMATION = 0x00000002
DACL_SECURITY_INFORMATION = 0x00000004
SACL_SECURITY_INFORMATION = 0x00000008
LABEL_SECURITY_INFORMATION = 0x00000010
ATTRIBUTE_SECURITY_INFORMATION = 0x00000020
SCOPE_SECURITY_INFORMATION = 0x00000040
PROCESS_TRUST_LABEL_SECURITY_INFORMATION = 0x00000080
BACKUP_SECURITY_INFORMATION = 0x00010000

PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
PROTECTED_SACL_SECURITY_INFORMATION = 0x40000000
UNPROTECTED_DACL_SECURITY_INFORMATION = 0x20000000
UNPROTECTED_SACL_SECURITY_INFORMATION = 0x10000000

GetFileSecurityW = BoolWinFunc("GetFileSecurityW", advapi32)
GetFileSecurityW.params = [
    InParam(LPWSTR, "lpFileName"),
    InParam(DWORD, "RequestedInformation"),
    ReturnOutParam(POINTER(SID), "pSecurityDescriptor", lambda: pointer(SID(0))),
    InParam(DWORD, "nLength", lambda: DWORD(sizeof(SID))),
    OutParam(POINTER(DWORD), "lpnLengthNeeded", lambda: pointer(DWORD(0)))
]

LookupAccountSidW = BoolWinFunc("LookupAccountSidW", advapi32)
LookupAccountSidW.params = [
    InParam(c_void_p, "system", lambda: None),
    InParam(c_void_p, "sid"),
    ReturnOutParam(LPWSTR, "name", lambda: create_unicode_buffer(512)),
    InOutParam(LPDWORD, "cchName", lambda: pointer(DWORD(512))),
    ReturnOutParam(LPWSTR, "domain", lambda: create_unicode_buffer(512)),
    InOutParam(LPDWORD, "cchDomain", lambda: pointer(DWORD(512))),
    ReturnOutParam(LPDWORD, "peUse", lambda: pointer(DWORD(0)))
]

MakeAbsoluteSD = BoolWinFunc("MakeAbsoluteSD", advapi32)
MakeAbsoluteSD.params = [
    InParam(c_void_p, "pSelfRelativeSD"),
    ReturnOutParam(c_void_p, "pAbsoluteSD", lambda: create_string_buffer(1024)),
    InOutParam(LPDWORD, "lpdwAbsoluteSDSize", lambda: DWORD(1024)),
    ReturnOutParam(c_void_p, "pDacl", lambda: create_string_buffer(1024)),
    InOutParam(LPDWORD, "lpdwDaclSize", lambda: DWORD(1024)),
    ReturnOutParam(c_void_p, "pSacl", lambda: create_string_buffer(1024)),
    InOutParam(LPDWORD, "lpdwSaclSize", lambda: DWORD(1024)),
    ReturnOutParam(c_void_p, "pOwner", lambda: create_string_buffer(256)),
    InOutParam(LPDWORD, "lpdwOwnerSize", lambda: DWORD(256)),
    ReturnOutParam(c_void_p, "pPrimaryGroup", lambda: create_string_buffer(256)),
    InOutParam(LPDWORD, "lpdwPrimaryGroupSize", lambda: DWORD(256)),
]