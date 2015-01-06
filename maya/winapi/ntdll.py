from maya.ctypeshelper import *
from maya.winapi.functions import WinapiWinFunc
from .types import *

ntdll = windll.ntdll

#
# NtQueryInformationProcess
#
class ProcessInformationClass:
    ProcessBasicInformation = 0
    ProcessDebugPort = 7
    ProcessWow64Information = 26
    ProcessImageFileName = 27
    ProcessBreakOnTermination = 29


class PROCESS_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("Reservd1", LPVOID),
        ("PebBaseAddress", LPVOID),
        ("Reserved2", LPVOID * 2),
        ("UniqueProcessId", ULONG),
        ("Reserved3", LPVOID)
    ]


class ProcessInformation(Union):
    _map_ = {
        ProcessInformationClass.ProcessBasicInformation: "BasicInformation",
        ProcessInformationClass.ProcessWow64Information: "fIsWow64",
        ProcessInformationClass.ProcessImageFileName: "ImageFileName"
    }

    _fields_ = [
        ("BasicInformation", PROCESS_BASIC_INFORMATION),
        ("fIsWow64", ULONG),
        ("ImageFileName", UNICODE_STRING)
    ]


_NtQueryInformationProcess = WinapiWinFunc("ZwQueryInformationProcess", ntdll)
_NtQueryInformationProcess.params = [
    InParam(HANDLE, "ProcessHandle"),
    InParam(DWORD, "ProcessInformationClass"),
    ReturnOutParam(POINTER(ProcessInformation), "ProcessInformation",
                   lambda: pointer(ProcessInformation()),
                   switch_is="ProcessInformationClass"),
    InParam(DWORD, "ProcessInformationLength", lambda: sizeof(ProcessInformation)),
    OutParam(DWORD, "ReturnLength", lambda: pointer(DWORD(0)))
]


#
# NtQuerySystemInformation
#
class SystemInformationClass:
    SystemBasicInformation = 0
    SystemPerformanceInformation = 2
    SystemTimeInformation = 3
    SystemProcessInformation = 5


class SYSTEM_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("Reserved", BYTE * 24),
        ("Reserved2", LPVOID * 4),
        ("NumberOfProcessors", c_ubyte)
    ]


class SYSTEM_PROCESS_INFORMATION(Structure):
    _fields_ = [
        ("NextEntryOffset", ULONG),
        ("NumberOfThreads", ULONG),
        ("Reserved1", BYTE * 48),
        ("Reserved2", LPVOID * 3),
        ("UniqueProcessId", HANDLE),
        ("Reserved3", LPVOID),
        ("HandleCount", ULONG),
        ("Reserved4", BYTE * 4),
        ("Reserved5", LPVOID * 11),
        ("PeakPagefileUsage", c_size_t),
        ("PrivatePageCount", c_size_t),
        ("Reserved6", LARGE_INTEGER * 6)
    ]


class SystemInformation(Union):
    _map_ = {
        SystemInformationClass.SystemBasicInformation: "BasicInformation",
        SystemInformationClass.SystemProcessInformation: "ProcessInformation"
    }

    _fields_ = [
        ("BasicInformation", SYSTEM_BASIC_INFORMATION),
        ("ProcessInformation", SYSTEM_PROCESS_INFORMATION)
    ]

_NtQuerySystemInformation = WinapiWinFunc("ZwQuerySystemInformation", ntdll)
_NtQuerySystemInformation.params = [
    InParam(DWORD, "SystemInformationClass"),
    ReturnInOutParam(POINTER(SystemInformation), "SystemInformation",
                     lambda: pointer(SystemInformation()),
                     switch_is="SystemInformationClass"),
    InParam(ULONG, "SystemInformationLength", lambda: sizeof(SystemInformation)),
    OutParam(PULONG, "ReturnLength", lambda: pointer(ULONG(0)))
]


class Ntdll:
    @staticmethod
    def NtQueryInformationProcess(handle, info_class):
        return _NtQueryInformationProcess(handle, info_class)

    @staticmethod
    def NtQuerySystemInformation(info_class):
        return _NtQuerySystemInformation(info_class)