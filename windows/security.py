#!/usr/bin/env python3

from ctypes import *
from ctypes.wintypes import *
from ctypeshelper.ctypeshelper import *
from ctypeshelper.windows import *

advapi32 = ctypes.windll.advapi32

# Constants
SECURITY_MAX_SID_SIZE = 68


TOKEN_ASSIGN_PRIMARY = 0x0001
TOKEN_DUPLICATE = 0x0002
TOKEN_IMPERSONATE = 0x0004
TOKEN_QUERY = 0x0008
TOKEN_QUERY_SOURCE = 0x0010
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS = 0x0040
TOKEN_ADJUST_DEFAULT = 0x0080
TOKEN_ADJUST_SESSIONID = 0x0100

# Types
SID = c_ubyte * SECURITY_MAX_SID_SIZE
PSID = POINTER(SID)
ACL = c_ubyte * 1024
PACL = POINTER(ACL)
SECURITY_DESCRIPTOR = c_ubyte * 1024

#
# Functions
#

# First param must be c_void_p to be received from output of SID producing functions
# as a bytes string and marshaled properly when passed to other functions
_ConvertSidToStringSidW = BoolWinFunc("ConvertSidToStringSidW", advapi32)
_ConvertSidToStringSidW.params = [
    InParam(c_void_p, "sid", None),
    ReturnOutParam(POINTER(LPWSTR), "string_sid", lambda: pointer(c_wchar_p(0)))
]

_CreateWellKnownSid = BoolWinFunc("CreateWellKnownSid", advapi32)
_CreateWellKnownSid.params = [
    InParam(DWORD, "WellKnownSidType"),
    InParam(c_void_p, "DomainSid", lambda: c_void_p(0)),
    ReturnOutParam(PSID, "pSid", lambda: pointer(SID(0))),
    InOutParam(LPDWORD, "cbSid", lambda: pointer(DWORD(SECURITY_MAX_SID_SIZE)))
]

_GetFileSecurityW = BoolWinFunc("GetFileSecurityW", advapi32)
_GetFileSecurityW.params = [
    InParam(LPWSTR, "lpFileName"),
    InParam(DWORD, "RequestedInformation"),
    ReturnOutParam(POINTER(SECURITY_DESCRIPTOR), "pSecurityDescriptor", lambda: pointer(SECURITY_DESCRIPTOR(0))),
    InParam(DWORD, "nLength", lambda: DWORD(sizeof(SECURITY_DESCRIPTOR))),
    OutParam(POINTER(DWORD), "lpnLengthNeeded", lambda: pointer(DWORD(0)))
]

# XP and later
_GetSecurityInfo = WinapiWinFunc("GetSecurityInfo", advapi32)
_GetSecurityInfo.params = [
    InParam(HANDLE, "handle"),
    InParam(c_ulong, "ObjectType"),
    InParam(DWORD, "SecurityInfo"),
    ReturnOutParam(POINTER(PSID), "ppSidOwner", lambda: pointer(PSID(0))),
    ReturnOutParam(POINTER(PSID), "ppSidGroup", lambda: pointer(PSID(0))),
    ReturnOutParam(POINTER(PACL), "ppDacl", lambda: pointer(PACL(0))),
    ReturnOutParam(POINTER(PACL), "ppSacl", lambda: pointer(PACL(0))),
    ReturnOutParam(POINTER(PSID), "ppSecurityDescriptor", lambda: pointer(PSID(0)))
]

_ImpersonateSelf = BoolWinFunc("ImpersonateSelf", advapi32)
_ImpersonateSelf.params = [
    InParam(DWORD, "ImpersonationLevel")
]

_LookupAccountSidW = BoolWinFunc("LookupAccountSidW", advapi32)
_LookupAccountSidW.params = [
    InParam(c_void_p, "system", lambda: None),
    InParam(c_void_p, "sid"),
    ReturnOutParam(LPWSTR, "name", lambda: create_unicode_buffer(512)),
    InOutParam(LPDWORD, "cchName", lambda: pointer(DWORD(512))),
    ReturnOutParam(LPWSTR, "domain", lambda: create_unicode_buffer(512)),
    InOutParam(LPDWORD, "cchDomain", lambda: pointer(DWORD(512))),
    ReturnOutParam(LPDWORD, "peUse", lambda: pointer(DWORD(0)))
]

_MakeAbsoluteSD = BoolWinFunc("MakeAbsoluteSD", advapi32)
_MakeAbsoluteSD.params = [
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

_OpenProcessToken = BoolWinFunc("OpenProcessToken", advapi32)
_OpenProcessToken.params = [
    InParam(HANDLE, "ProcessHandle"),
    InParam(DWORD, "DesiredAccess"),
    ReturnOutParam(POINTER(HANDLE), "TokenHandle", lambda: pointer(HANDLE(0)))
]

_OpenThreadToken = BoolWinFunc("OpenThreadToken", advapi32)
_OpenThreadToken.params = [
    InParam(HANDLE, "ThreadHandle"),
    InParam(DWORD, "DesiredAccess"),
    InParam(BOOL, "OpenAsSelf"),
    ReturnOutParam(PHANDLE, "TokenHandle", pointer(HANDLE(0)))
]

_RevertToSelf = BoolWinFunc("RevertToSelf", advapi32)


class Advapi32:
    #
    # Constants
    #
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

    SECURITY_MAX_SID_SIZE = 68

    WinNullSid = 0

    #
    # Types
    #
    SID = c_ubyte * SECURITY_MAX_SID_SIZE
    PSID = POINTER(SID)

    #
    # APIs
    #
    ConvertSidToStringSidW = _ConvertSidToStringSidW
    CreateWellKnownSid = _CreateWellKnownSid
    GetFileSecurityW = _GetFileSecurityW
    GetSecurityInfo = _GetSecurityInfo
    ImpersonateSelf = _ImpersonateSelf
    LookupAccountSidW = _LookupAccountSidW
    # MakeAbsoluteSD = _MakeAbsoluteSD
    OpenProcessToken = _OpenProcessToken
    OpenThreadToken = _OpenThreadToken
    RevertToSelf = _RevertToSelf

