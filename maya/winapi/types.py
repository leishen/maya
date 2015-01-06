from ctypes import *
from ctypes.wintypes import *
from maya.ctypeshelper import AutoStructure


class UNICODE_STRING(Structure):
    _fields_ = [
        ("Length", USHORT),
        ("MaximumLength", USHORT),
        ("Buffer", LPWSTR)
    ]

MAX_PATH = 0x104
max_path_wstr = WCHAR * MAX_PATH
max_path_str = CHAR * MAX_PATH


class ProcessAccessRights:
    PROCESS_QUERY_INFORMATION = 0x0400


class PROCESSENTRY32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("cntUsage", DWORD),
        ("th32ProcessID", DWORD),
        ("th32DefaultHeapID", c_void_p),
        ("th32ModuleID", DWORD),
        ("cntThreads", DWORD),
        ("th32ParentProcessID", DWORD),
        ("pcPriClassBase", LONG),
        ("dwFlags", DWORD),
        ("szExeFile", c_char * 0x104)
    ]


class MODULEENTRY32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("th32ModuleID", DWORD),
        ("th32ProcessID", DWORD),
        ("GlblcntUsage", DWORD),
        ("ProccntUsage", DWORD),
        ("modBaseAddr", c_void_p),
        ("modBaseSize", DWORD),
        ("hModule", HMODULE),
        ("szModule", c_char * (255 + 1)),
        ("szExePath", c_char * 0x104)
    ]


class THREADENTRY32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("cntUsage", DWORD),
        ("th32ThreadID", DWORD),
        ("th32OwnerProcessID", DWORD),
        ("tpBasePri", LONG),
        ("tpDeltaPri", LONG),
        ("dwFlags", DWORD)
    ]



# Constants
SECURITY_MAX_SID_SIZE = 68

# Types
SID = c_ubyte * SECURITY_MAX_SID_SIZE
PSID = POINTER(SID)
ACL = c_ubyte * 1024
PACL = POINTER(ACL)
SECURITY_DESCRIPTOR = c_ubyte * 1024


class _LUID(Structure):
    _fields_ = [
        ("LowPart", DWORD),
        ("HighPart", LONG)
    ]

LUID = c_ubyte * sizeof(_LUID)


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


class Toolhelp32Flags:
    TH32CS_INHERIT = 0x80000000
    TH32CS_SNAPHEAPLIST = 0x00000001
    TH32CS_SNAPPROCESS = 0x00000002
    TH32CS_SNAPTHREAD = 0x00000004
    TH32CS_SNAPMODULE = 0x00000008
    TH32CS_SNAPMODULE32 = 0x00000010
    TH32CS_SNAPALL = 0x0000001f     # Combination of all other flags