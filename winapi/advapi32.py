#!/usr/bin/env python3

from ctypes import *
from ctypes.wintypes import *
from ctypeshelper import *
from .functions import BoolWinFunc, WinapiWinFunc


__all__ = ['Advapi32', 'TokenPrivileges', 'WellKnownSidTypes', 'SecurityInformation', 'SECURITY_MAX_SID_SIZE',
           'TokenAccessRights', 'TOKEN_INFORMATION_CLASS']


advapi32 = ctypes.windll.advapi32

# Constants
SECURITY_MAX_SID_SIZE = 68

# Types
SID = c_ubyte * SECURITY_MAX_SID_SIZE
PSID = POINTER(SID)
ACL = c_ubyte * 1024
PACL = POINTER(ACL)
SECURITY_DESCRIPTOR = c_ubyte * 1024


# TODO GetTokenInformation needs a union of all possible structures
class LUID(Structure):
    _fields_ = [
        ("LowPart", DWORD),
        ("HighPart", LONG)
    ]


class SID_AND_ATTRIBUTES(Structure):
    _fields_ = [
        ("Sid", PSID),
        ("Attributes", DWORD)
    ]


class LUID_AND_ATTRIBUTES(Structure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", DWORD)
    ]


class TOKEN_GROUPS(Structure):
    _fields_ = [
        ("GropuCount", DWORD),
        ("Groups", SID_AND_ATTRIBUTES * 64)             # Arbitrarily chose a size.  Should be ANYSIZE_ARRAY
    ]


class TOKEN_PRIVILEGES(Structure):
    _fields_ = [
        ("PrivilegeCount", DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 64)        # Arbitrarily chose a size.  Should be ANYSIZE_ARRAY
    ]


class TOKEN_USER(Structure):
    _fields_ = [
        ("User", SID_AND_ATTRIBUTES)
    ]


class TOKEN_INFORMATION_CLASS:
    (TokenUser,
     TokenGroups,
     TokenPrivileges,
     TokenOwner,
     TokenPrimaryGroup,
     TokenDefaultDacl,
     TokenSource,
     TokenType,
     TokenImpersonationLevel,
     TokenStatistics,
     TokenRestrictedSids,
     TokenSessionId,
     TokenGroupsAndPrivileges,
     TokenSessionReference,
     TokenSandBoxInert,
     TokenAuditPolicy,
     TokenOrigin,
     TokenElevationType,
     TokenLinkedToken,
     TokenElevation,
     TokenHasRestrictions,
     TokenAccessInformation,
     TokenVirtualizationAllowed,
     TokenVirtualizationEnabled,
     TokenIntegrityLevel,
     TokenUIAccess,
     TokenMandatoryPolicy,
     TokenLogonSid,
     TokenIsAppContainer,
     TokenCapabilities,
     TokenAppContainerSid,
     TokenAppContainerNumber,
     TokenUserClaimAttributes,
     TokenDeviceClaimAttributes,
     TokenRestrictedUserClaimAttributes,
     TokenRestrictedDeviceClaimAttributes,
     TokenDeviceGroups,
     TokenRestrictedDeviceGroups,
     TokenSecurityAttributes,
     TokenIsRestricted,
     MaxTokenInfoClass) = list(range(1, 42))


class WellKnownSidType:
    WinNullSid = 0


class TokenInformation(Union):
    _map_ = {
        TOKEN_INFORMATION_CLASS.TokenUser: "TokenUser",
        TOKEN_INFORMATION_CLASS.TokenPrivileges: "TokenPrivileges",
        TOKEN_INFORMATION_CLASS.TokenGroups: "TokenGroups",
        TOKEN_INFORMATION_CLASS.TokenImpersonationLevel: "TokenImpersonationLevel",
        TOKEN_INFORMATION_CLASS.TokenSessionId: "TokenSessionId"
    }

    _fields_ = [
        ("TokenUser", TOKEN_USER),
        ("TokenPrivileges", TOKEN_PRIVILEGES),
        ("TokenGroups", TOKEN_GROUPS),
        ("TokenImpersonationLevel", DWORD),
        ("TokenSessionId", DWORD)
    ]


class TokenAccessRights:
    TOKEN_ASSIGN_PRIMARY = 0x0001
    TOKEN_DUPLICATE = 0x0002
    TOKEN_IMPERSONATE = 0x0004
    TOKEN_QUERY = 0x0008
    TOKEN_QUERY_SOURCE = 0x0010
    TOKEN_ADJUST_PRIVILEGES = 0x0020
    TOKEN_ADJUST_GROUPS = 0x0040
    TOKEN_ADJUST_DEFAULT = 0x0080
    TOKEN_ADJUST_SESSIONID = 0x0100


class TokenPrivileges:
    TOKEN_ASSIGN_PRIMARY = 0x0001
    TOKEN_DUPLICATE = 0x0002
    TOKEN_IMPERSONATE = 0x0004
    TOKEN_QUERY = 0x0008
    TOKEN_QUERY_SOURCE = 0x0010
    TOKEN_ADJUST_PRIVILEGES = 0x0020
    TOKEN_ADJUST_GROUPS = 0x0040
    TOKEN_ADJUST_DEFAULT = 0x0080
    TOKEN_ADJUST_SESSIONID = 0x0100


class SecurityInformation:
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
    ReturnOutParam(PSID, "pSid", lambda: pointer(SID())),
    InOutParam(LPDWORD, "cbSid", lambda: pointer(DWORD(SECURITY_MAX_SID_SIZE)))
]

_GetFileSecurityW = BoolWinFunc("GetFileSecurityW", advapi32)
_GetFileSecurityW.params = [
    InParam(LPWSTR, "lpFileName"),
    InParam(DWORD, "RequestedInformation"),
    ReturnOutParam(POINTER(SECURITY_DESCRIPTOR), "pSecurityDescriptor", lambda: pointer(SECURITY_DESCRIPTOR())),
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

_GetTokenInformation = BoolWinFunc("GetTokenInformation", advapi32)
_GetTokenInformation.params = [
    InParam(HANDLE, "TokenHandle"),
    InParam(DWORD, "TokenInformationClass"),
    ReturnOutParam(POINTER(TokenInformation), "TokenInformation",
                   lambda: pointer(TokenInformation()),
                   switch_is="TokenInformationClass"),
    InParam(DWORD, "TokenInformationLength", lambda: 1024),
    OutParam(PDWORD, "ReturnLength", lambda: pointer(DWORD(0)))
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
    ReturnOutParam(POINTER(HANDLE), "TokenHandle", lambda: pointer(HANDLE()))
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
    """ctypes implementations of Security-related APIs from advapi32.dll"""
    @staticmethod
    def ConvertSidToStringSidW(sid) -> str:
        """Converts a security identifier (SID) to a string format suitable for display, storage, or transmission.

        :param sid: Binary security identifier, as a bytes string
        :return: str represening the SID as a string"""
        return _ConvertSidToStringSidW(sid)

    @staticmethod
    def CreateWellKnownSid(WellKnownSidType) -> SID:
        """Creates a SID for predefined aliases

        :param WellKnownSidType: Specifies what the SID will identify, values defined in the WellKnownSidType class
        :return: SID
        """
        return _CreateWellKnownSid(WellKnownSidType)

    @staticmethod
    def GetFileSecurityW(lpFileName, RequestedInformation) -> bytes:
        """Obtains specified information about the security of a file or directory. The information obtained is
        constrained by the caller's access rights and privileges.

        :param lpFileName: File or directory for which security information is retrieved
        :param RequestedInformation: value that identifies the security information being requested, from
                                     SecurityInformation
        :return: Security descriptor, as a bytes string
        """
        return _GetFileSecurityW(lpFileName, RequestedInformation)

    @staticmethod
    def GetSecurityInfo(handle, ObjectType, SecurityInfo):
        """Retrieves a copy of the security descriptor for an object specified by a handle

        :param handle: Handle to an object
        :param ObjectType: SE_OBJECT_TYPE enumeration value that indicates the type of object
        :param SecurityInfo:  type of security information to retrieve

        :return:  -> (owner, group, dacl, sacl, security_descriptor)
        """
        return _GetSecurityInfo(handle, ObjectType, SecurityInfo)

    @staticmethod
    def GetTokenInformation(handle, TokenInformationClass):
        return _GetTokenInformation(handle, TokenInformationClass)

    @staticmethod
    def ImpersonateSelf():
        """Obtains an access token that impersonates the security context of the calling process. The token is
        assigned to the calling thread.
        """
        return _ImpersonateSelf()

    @staticmethod
    def LookupAccountSidW(sid, system=None):
        """Retrieve the name of the account for a SID and the name of the first domain on which this SID is found

        :param sid: The SID (as a bytes array) to identify
        :param system: The system on which to search.  None defaults to the local computer

        :return: (name, domain, sid_name_use)
        """
        return _LookupAccountSidW(system, sid)

    # MakeAbsoluteSD = _MakeAbsoluteSD
    @staticmethod
    def OpenProcessToken(ProcessHandle, DesiredAccess):
        """Opens the access token associated with a process

        :param ProcessHandle: A handle to the process whose access token is opened. The process must have the
                              PROCESS_QUERY_INFORMATION access permission
        :param DesiredAccess: Specifies an access mask that specifies the requested types of access to the access token
        :return: Handle to the process token, as an int
        """
        return _OpenProcessToken(ProcessHandle, DesiredAccess)

    @staticmethod
    def OpenThreadToken(ThreadHandle, DesiredAccess, OpenAsSelf=True):
        """Opens the access token associated with a thread

        :param ThreadHandle: A handle to the thread whose access token is opened.
        :param DesiredAccess: Specifies an access mask that specifies the requested types of access to the access token.
        :param OpenAsSelf: TRUE if the access check is to be made against the process-level security context.
                           FALSE if the access check is to be made against the current security context of the thread
                           calling the OpenThreadToken function.
        :return: Handle to the thread token, as an int
        """
        return _OpenThreadToken(ThreadHandle, DesiredAccess, OpenAsSelf)

    @staticmethod
    def RevertToSelf():
        """Terminates the impersonation of a client application"""
        return _RevertToSelf()

