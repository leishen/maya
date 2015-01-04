from maya.ctypeshelper import *
from maya.winapi.functions import WinapiWinFunc
from .types import *

ntdll = windll.ntdll

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