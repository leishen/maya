#!/usr/bin/env python3

from ctypes import *
from ctypes.wintypes import *

from maya.ctypeshelper import *
from maya.winapi.functions import BoolWinFunc, WinapiWinFunc, trace


__all__ = ['Advapi32', 'TokenPrivileges', 'WellKnownSidTypes', 'SecurityInformation', 'SECURITY_MAX_SID_SIZE',
           'TokenInformationClass',
           'TOKEN_PRIVILEGES']


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
#class LUID(Structure):
#    _fields_ = [
#        ("LowPart", DWORD),
#        ("HighPart", LONG)
#    ]
LUID = c_ubyte * 8

class SID_AND_ATTRIBUTES(AutoStructure):
    _fields_ = [
        ("Sid", PSID),
        ("Attributes", DWORD)
    ]


class LUID_AND_ATTRIBUTES(AutoStructure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", DWORD)
    ]


class TOKEN_GROUPS(AutoStructure):
    _fields_ = [
        ("GropuCount", DWORD),
        ("Groups", SID_AND_ATTRIBUTES * 64)             # Arbitrarily chose a size.  Should be ANYSIZE_ARRAY
    ]


class TOKEN_PRIVILEGES(AutoStructure):
    _fields_ = [
        ("PrivilegeCount", DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 64)        # Arbitrarily chose a size.  Should be ANYSIZE_ARRAY
    ]


class TOKEN_USER(AutoStructure):
    _fields_ = [
        ("User", SID_AND_ATTRIBUTES)
    ]


class TokenInformationClass:
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


class WellKnownSidTypes:
    WinNullSid = 0


class TokenInformation(Union):
    _map_ = {
        TokenInformationClass.TokenUser: "TokenUser",
        TokenInformationClass.TokenPrivileges: "TokenPrivileges",
        TokenInformationClass.TokenGroups: "TokenGroups",
        TokenInformationClass.TokenImpersonationLevel: "TokenImpersonationLevel",
        TokenInformationClass.TokenSessionId: "TokenSessionId"
    }

    _fields_ = [
        ("TokenUser", TOKEN_USER),
        ("TokenPrivileges", TOKEN_PRIVILEGES),
        ("TokenGroups", TOKEN_GROUPS),
        ("TokenImpersonationLevel", DWORD),
        ("TokenSessionId", DWORD)
    ]


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
_AdjustTokenPrivileges = BoolWinFunc("AdjustTokenPrivileges", advapi32)
_AdjustTokenPrivileges.params = [
    InParam(HANDLE, "TokenHandle"),
    InParam(BOOL, "DisableAllPrivileges", lambda: False),
    InParam(POINTER(TOKEN_PRIVILEGES), "NewState"),
    InParam(DWORD, "BufferLength", lambda: sizeof(TOKEN_PRIVILEGES())),
    ReturnOutParam(POINTER(TOKEN_PRIVILEGES), "PreviousState", lambda: pointer(TOKEN_PRIVILEGES())),
    OutParam(PDWORD, "ReturnLength", lambda: pointer(DWORD(0)))
]

# First param must be c_void_p to be received from output of SID producing functions
# as a bytes string and marshaled properly when passed to other functions
_ConvertSidToStringSidW = BoolWinFunc("ConvertSidToStringSidW", advapi32)
_ConvertSidToStringSidW.params = [
    InParam(c_void_p, "sid", None),
    ReturnOutParam(POINTER(LPWSTR), "string_sid", lambda: pointer(c_wchar_p(0)))
]

_ConvertStringSidToSidW = BoolWinFunc("ConvertStringSidToSidW", advapi32)
_ConvertStringSidToSidW.params = [
    InParam(LPWSTR, "StringSid"),
    ReturnOutParam(PSID, "Sid", lambda: pointer(SID()))
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
    InParam(DWORD, "TokenInformationLength", lambda: sizeof(TokenInformation)),
    OutParam(PDWORD, "ReturnLength", lambda: pointer(DWORD(0)))
]

_ImpersonateSelf = BoolWinFunc("ImpersonateSelf", advapi32)
_ImpersonateSelf.params = [
    InParam(DWORD, "ImpersonationLevel")
]

_LookupAccountNameW = BoolWinFunc("LookupAccountNameW", advapi32)
_LookupAccountNameW.params = [
    InParam(c_void_p, "system", lambda: None),
    InParam(LPCSTR, "lpAccountName"),
    ReturnOutParam(PSID, "sid", lambda: pointer(SID())),
    InOutParam(LPDWORD, "cbSid", lambda: pointer(sizeof(SID))),
    ReturnOutParam(LPWSTR, "domain", lambda: create_unicode_buffer(512)),
    InOutParam(LPDWORD, "cchDomain", lambda: pointer(DWORD(512))),
    ReturnOutParam(LPDWORD, "peUse", lambda: pointer(DWORD(0)))
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

# lpLuid must be a c_void_p to take a byte array representing a LUID
_LookupPrivilegeNameW = BoolWinFunc("LookupPrivilegeNameW", advapi32)
_LookupPrivilegeNameW.params = [
    InParam(LPWSTR, "lpSystemName", lambda: None),
    InParam(c_void_p, "lpLuid"),
    ReturnOutParam(LPWSTR, "lpName", lambda: create_unicode_buffer(MAX_PATH)),
    InOutParam(LPDWORD, "cchName", lambda: pointer(DWORD(MAX_PATH)))
]

_LookupPrivilegeValueW = BoolWinFunc("LookupPrivilegeValueW", advapi32)
_LookupPrivilegeValueW.params = [
    InParam(c_void_p, "lpSystemName", lambda: None),
    InParam(LPWSTR, "lpName"),
    ReturnOutParam(POINTER(LUID), "lpLuid", lambda: pointer(LUID()))
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
    ReturnOutParam(PHANDLE, "TokenHandle", lambda: pointer(HANDLE()))
]

_RevertToSelf = BoolWinFunc("RevertToSelf", advapi32)


class Advapi32:
    """ctypes implementations of Security-related APIs from advapi32.dll"""
    @staticmethod
    def AdjustTokenPrivileges(handle,
                              new_state: TOKEN_PRIVILEGES,
                              disable_all: bool=False):
        # What happens if I just pass the structure?
        # TODO Have to marshall the parameter
        return _AdjustTokenPrivileges(handle, disable_all, new_state)

    @staticmethod
    def ConvertSidToStringSidW(sid) -> str:
        """Converts a security identifier (SID) to a string format suitable for display, storage, or transmission.

        :param sid: Binary security identifier, as a bytes string
        :return: str represening the SID as a string"""
        return _ConvertSidToStringSidW(sid)

    @staticmethod
    def ConvertStringSidToSidW(sid) -> bytes:
        """converts a string-format security identifier (SID) into a valid, functional SID.

        :param sid:  the string-format SID to convert.
        :return: The binary sid corresponding to the string argument
        """
        return _ConvertStringSidToSidW(sid)

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
    @trace
    def GetTokenInformation(handle, TokenInformationClass):
        return _GetTokenInformation(handle, TokenInformationClass)

    @staticmethod
    def ImpersonateSelf():
        """Obtains an access token that impersonates the security context of the calling process. The token is
        assigned to the calling thread.
        """
        return _ImpersonateSelf()

    @staticmethod
    def LookupAccountNameW(name, system=None):
        """The LookupAccountName function accepts the name of a system and an account as input. It retrieves a
        security identifier (SID) for the account and the name of the domain on which the account was found.

        :param name:  the account name.  A fully qualified (domain\\name) name will yield best results
        :return: The sid for the corresponding name
        """
        return _LookupAccountSidW(system, name)

    @staticmethod
    def LookupAccountSidW(sid, system=None):
        """Retrieve the name of the account for a SID and the name of the first domain on which this SID is found

        :param sid: The SID (as a bytes array) to identify
        :param system: The system on which to search.  None defaults to the local computer

        :return: (name, domain, sid_name_use)
        """
        return _LookupAccountSidW(system, sid)

    @staticmethod
    def LookupPrivilegeNameW(luid: bytes, system: str=None):
        """Retrieves the name that corresponds to the privilege represented on a specific system by a specified
        locally unique identifier (LUID).

        :param luid: the LUID by which the privilege is known on the target system.
        :param system: The name of the system on which the privilege name is retrieved
        :return: String representing the binary LUID
        """
        return _LookupPrivilegeNameW(system, luid)

    @staticmethod
    def LookupPrivilegeValueW(name, system=None):
        """Retrieves the locally unique identifier (LUID) used on a specified system to locally represent the
        specified privilege name.

        :param name: The name of the privilege, as defined in the Winnt.h header file.
        :param system: The name of the system on which the privilege name is retrieved
        :return: The LUID, as a byte string
        """
        return _LookupPrivilegeValueW(system, name)

    # MakeAbsoluteSD = _MakeAbsoluteSD
    @staticmethod
    @trace
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

