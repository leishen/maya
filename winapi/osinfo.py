from .kernel32 import *
from .advapi32 import *
from ctypes.wintypes import *


class Thread:
    def __init__(self):
        pass


class Process:
    def __init__(self, name, pid, parent_pid=0):
        self._name = name
        self._pid = pid
        self._parent_pid = parent_pid

    def _get_token(self):
        PROCESS_QUERY_INFORMATION = 0x0400
        hProc = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, self._pid)
        hToken = Advapi32.OpenProcessToken(hProc, TokenAccessRights.TOKEN_QUERY)
        return hToken

    @property
    def user(self):
        hToken = self._get_token()


    @property
    def modules(self):
        snap = Kernel32.CreateToolhelp32Snapshot(Toolhelp32Flags.TH32CS_SNAPMODULE, self._pid)
        module = Kernel32.Module32First(snap)
        yield module
        while True:
            try:
                module = Kernel32.Module32Next(snap)
                yield module
            except OSError:
                break

    @property
    def parent_pid(self):
        return self._parent_pid

    @property
    def threads(self):
        snap = Kernel32.CreateToolhelp32Snapshot(Toolhelp32Flags.TH32CS_SNAPTHREAD, self._pid)
        thread = Kernel32.Thread32First(snap)
        yield thread
        while True:
            try:
                thread = Kernel32.Thread32Next(snap)
                yield thread
            except OSError:
                break


class ProcessSnapshot:
    def __init__(self):
        self._hSnapshot = Kernel32.CreateToolhelp32Snapshot(Toolhelp32Flags.TH32CS_SNAPPROCESS)

    def __enter__(self):
        return self

    def __exit__(self):
        Kernel32.CloseHandle(self._hSnapshot)

    @property
    def processes(self):
        proc = Kernel32.Process32First(self._hSnapshot)
        yield proc
        while True:
            try:
                proc = Kernel32.Process32Next(self._hSnapshot)
                yield proc
            except OSError:
                break


