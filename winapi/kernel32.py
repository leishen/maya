from ctypeshelper import *
from .functions import BoolWinFunc, HandleWinFunc
from ctypes import Structure, c_void_p, c_char, pointer, POINTER, sizeof
from ctypes.wintypes import DWORD, HANDLE, LONG, HMODULE
import ctypes


kernel32 = ctypes.windll.kernel32


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


_CloseHandle = BoolWinFunc("CloseHandle", kernel32)
_CloseHandle.params = [
    InParam(HANDLE, "handle")
]

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


class Toolhelp32Flags:
    TH32CS_INHERIT = 0x80000000
    TH32CS_SNAPHEAPLIST = 0x00000001
    TH32CS_SNAPPROCESS = 0x00000002
    TH32CS_SNAPTHREAD = 0x00000004
    TH32CS_SNAPMODULE = 0x00000008
    TH32CS_SNAPMODULE32 = 0x00000010
    TH32CS_SNAPALL = 0x0000001f     # Combination of all other flags


class Kernel32:
    @staticmethod
    def CloseHandle(handle):
        return _CloseHandle(handle)

    @staticmethod
    def CreateToolhelp32Snapshot(flags, pid=0):
        return _CreateToolhelp32Snapshot(flags, pid)

    @staticmethod
    def Module32First(hSnapshot):
        return _Module32First(hSnapshot)

    @staticmethod
    def Module32Next(hSnapshot):
        return _Module32Next(hSnapshot)

    @staticmethod
    def Process32First(hSnapshot):
        return _Process32First(hSnapshot)

    @staticmethod
    def Process32Next(hSnapshot):
        return _Process32Next(hSnapshot)

    @staticmethod
    def Thread32First(hSnapshot):
        return _Thread32First(hSnapshot)

    @staticmethod
    def Thread32Next(hSnapshot):
        return _Thread32Next(hSnapshot)

