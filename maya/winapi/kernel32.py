from maya.ctypeshelper import *
from maya.winapi.functions import BoolWinFunc, HandleWinFunc, WinapiWinFunc, trace
from .types import *

__all__ = ['Kernel32']

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

_CloseHandle = BoolWinFunc("CloseHandle", kernel32)
_CloseHandle.params = [
    InParam(HANDLE, "handle")
]

_OpenProcess = HandleWinFunc("OpenProcess", kernel32)
_OpenProcess.params = [
    InParam(DWORD, "dwDesiredaccess"),
    InParam(BOOL, "bInheritHandle", lambda: False),
    InParam(DWORD, "dwProcessId")
]

# This can sometimes be in psapi.dll instead of kernel32
try:
    _GetProcessImageFileNameW = WinapiWinFunc("GetProcessImageFileNameW", kernel32)
except AttributeError:
    _GetProcessImageFileNameW = WinapiWinFunc("GetProcessImageFileNameW", psapi)
_GetProcessImageFileNameW.params = [
    InParam(HANDLE, "hProcess"),
    ReturnOutParam(LPWSTR, "lpImageFileName", lambda: pointer(max_path_wstr())),
    InParam(DWORD, "nSize",  sizeof(max_path_wstr()))
]

#
# Toolhelp32 API
#
_CreateToolhelp32Snapshot = HandleWinFunc("CreateToolhelp32Snapshot", kernel32)
_CreateToolhelp32Snapshot.params = [
    InParam(DWORD, "dwFlags"),
    InParam(DWORD, "th32ProcessId")
]

_Module32First = BoolWinFunc("Module32First", kernel32)
_Module32First.params = [
    InParam(HANDLE, "hSnapshot"),
    ReturnInOutParam(POINTER(MODULEENTRY32), "lpme", lambda: pointer(MODULEENTRY32(dwSize=sizeof(MODULEENTRY32))))
]

_Module32Next = BoolWinFunc("Module32Next", kernel32)
_Module32Next.params = [
    InParam(HANDLE, "hSnapshot"),
    ReturnInOutParam(POINTER(MODULEENTRY32), "lpme", lambda: pointer(MODULEENTRY32(dwSize=sizeof(MODULEENTRY32))))
]

_Process32First = BoolWinFunc("Process32First", kernel32)
_Process32First.params = [
    InParam(HANDLE, "hSnapshot"),
    ReturnInOutParam(POINTER(PROCESSENTRY32), "lppe", lambda: pointer(PROCESSENTRY32(dwSize=sizeof(PROCESSENTRY32))))
]

_Process32Next = BoolWinFunc("Process32Next", kernel32)
_Process32Next.params = [
    InParam(HANDLE, "hSnapshot"),
    ReturnInOutParam(POINTER(PROCESSENTRY32), "lppe", lambda: pointer(PROCESSENTRY32(dwSize=sizeof(PROCESSENTRY32))))
]

_Thread32First = BoolWinFunc("Thread32First", kernel32)
_Thread32First.params = [
    InParam(HANDLE, "hSnapshot"),
    ReturnInOutParam(POINTER(THREADENTRY32), "lpte", lambda: pointer(THREADENTRY32(dwSize=sizeof(THREADENTRY32))))
]

_Thread32Next = BoolWinFunc("Thread32Next", kernel32)
_Thread32Next.params = [
    InParam(HANDLE, "hSnapshot"),
    ReturnInOutParam(POINTER(THREADENTRY32), "lpte", lambda: pointer(THREADENTRY32(dwSize=sizeof(THREADENTRY32))))
]


class Kernel32:
    @staticmethod
    def CloseHandle(handle):
        """Closes an open object handle

        :param handle: A valid handle to an open object.
        """
        return _CloseHandle(handle)

    @staticmethod
    @trace
    def OpenProcess(pid, access=ProcessAccessRights.PROCESS_QUERY_INFORMATION):
        """Opens an existing local process object.

        :param pid: PID of the target process
        :param access: The access to the process object.
        :return: HANDLE to the target process
        """
        return _OpenProcess(access, dwProcessId=pid)

    @staticmethod
    def GetProcessImageFileNameW(handle):
        return _GetProcessImageFileNameW(handle)

    @staticmethod
    def CreateToolhelp32Snapshot(flags, pid=0):
        """Takes a snapshot of the specified processes, as well as the heaps, modules, and
        threads used by these processes.

        :param flags: The portions of the system to be included in the snapshot.
        :param pid: The process identifier of the process to be included in the snapshot. This parameter can be zero
            to indicate the current process.
        :return: Handle to a snapshot
        """
        return _CreateToolhelp32Snapshot(flags, pid)

    @staticmethod
    def Module32First(hSnapshot):
        """Retrieves information about the first module associated with a process.

        :param hSnapshot: The handle obtained by CreateToolhelp32Snapshot
        :return: MODULEENTRY32 structure, as a dictionary
        """
        return _Module32First(hSnapshot)

    @staticmethod
    def Module32Next(hSnapshot):
        """Retrieves information about the next module associated with a process or thread.

        :param hSnapshot: A handle to the snapshot returned from a previous call to the CreateToolhelp32Snapshot
            function.
        :return: MODULEENTRY32 structure, as a dictionary
        """
        return _Module32Next(hSnapshot)

    @staticmethod
    def Process32First(hSnapshot):
        """Retrieves information about the first process encountered in a system snapshot.

        :param hSnapshot: A handle to the snapshot returned from a previous call to the CreateToolhelp32Snapshot function.
        :return: PROCESSENTRY32 structure, as a dictionary
        """
        return _Process32First(hSnapshot)

    @staticmethod
    def Process32Next(hSnapshot):
        """Retrieves information about the next process recorded in a system snapshot

        :param hSnapshot: A handle to the snapshot returned from a previous call to the CreateToolhelp32Snapshot function.
        :return: PROCESSENTRY32 structure, as a dictionary
        """
        return _Process32Next(hSnapshot)

    @staticmethod
    def Thread32First(hSnapshot):
        """Retrieves information about the first thread of any process encountered in a system snapshot.

        :param hSnapshot: A handle to the snapshot returned from a previous call to the CreateToolhelp32Snapshot function.
        :return: THREADENTRY32 structure, as a dictionary
        """
        return _Thread32First(hSnapshot)

    @staticmethod
    def Thread32Next(hSnapshot):
        """Retrieves information about the next thread of any process encountered in a system snapshot.

        :param hSnapshot: A handle to the snapshot returned from a previous call to the CreateToolhelp32Snapshot function.
        :return: THREADENTRY32 structure, as a dictionary
        """
        return _Thread32Next(hSnapshot)

