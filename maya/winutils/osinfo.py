from ctypes import windll
from collections import namedtuple
from maya.winapi.kernel32 import *
from maya.winapi.advapi32 import *


Privilege = namedtuple('Privilege', ['name', 'luid', 'attributes'])


class Principal:
    def __init__(self, name=None, sid=None):
        if sid:
            if not isinstance(sid, str):
                self._binary_sid = sid
                self._sid = Advapi32.ConvertSidToStringSidW(sid)
            else:
                self._sid = sid
                self._binary_sid = Advapi32.ConvertStringSidToSidW(sid)
        self._name = name
        # Check for \ or @ in name to get domain
        self._domain = None

    def __str__(self):
        u = namedtuple('Principal', ['sid', 'name', 'domain'])
        user = u(self.sid, self.name, self.domain)
        return str(user)

    @property
    def name(self):
        if not self._name:
            self._name, self._domain, snu = Advapi32.LookupAccountSidW(self._binary_sid)
        return self._name

    @property
    def sid(self):
        if not self._binary_sid:
            # Get the sid
            self._binary_sid, domain, snu = Advapi32.LookupAccountNameW(self.name)
            self._sid = Advapi32.ConvertSidToStringSidW(self._binary_sid)
        return self._sid

    @property
    def domain(self):
        if not self._domain:
            self._name, self._domain, snu = Advapi32.LookupAccountSidW(self._binary_sid)
        return self._domain


class Token:
    def __init__(self, hToken):
        self._hToken = hToken
        self._user = None
        self._session_id = None
        self._groups = None

    @property
    def user(self) -> Principal:
        if not self._user:
            self._user = Advapi32.GetTokenInformation(self._hToken,
                TokenInformationClass.TokenUser)
        u = Principal(sid=self._user['User']['Sid'])
        return u

    @property
    def session_id(self) -> int:
        if not self._session_id:
            self._session_id = Advapi32.GetTokenInformation(self._hToken, TokenInformationClass.TokenSessionId)
        return self._session_id

    @property
    def groups(self):
        # TODO Groups causes access violation
        #if not self._groups:
        #    self._groups = Advapi32.GetTokenInformation(self._hToken, TokenInformationClass.TokenGroups)
        #return self._groups
        return None

    def close(self):
        Kernel32.CloseHandle(self._hToken)

    def __str__(self):
        t = namedtuple('Token', ['user', 'session_id', 'groups', 'privileges'])
        return str(t(self.user, self.session_id, self.groups, self.privileges))
        #return str(t(str(self.user), self.session_id, None, list(self.privileges)))

    def __del__(self):
        self.close()

    @property
    def privileges(self):
        privileges = Advapi32.GetTokenInformation(self._hToken, TokenInformationClass.TokenPrivileges)
        # logging.debug("Count: {0}".format(privileges['PrivilegeCount']))
        for i in range(0, privileges['PrivilegeCount']):
            p = privileges['Privileges'][i]
            print(str(p))
            name = Advapi32.LookupPrivilegeNameW(p['Luid'])
            yield Privilege(name, p['Luid'], p['Attributes'])

    def enable_privilege(self, priv):
        if isinstance(priv, Privilege):
            priv = priv.name
        luid = Advapi32.LookupPrivilegeValueW(priv)
        p = TOKEN_PRIVILEGES()
        p.PrivilegeCount = 1
        p.Privileges = [{
            'Luid': luid,
            'Attributes': 1
        }]
        Advapi32.AdjustTokenPrivileges(self._hToken, p)

    def disable_privilege(self, priv):
        if isinstance(priv, Privilege):
            priv = priv.name
        luid = Advapi32.LookupPrivilegeValueW(priv)
        p = TOKEN_PRIVILEGES()
        p.PrivilegeCount = 1
        p.Privileges[0].Luid = luid
        p.Privileges[0].Attributes = 0
        Advapi32.AdjustTokenPrivileges(self._hToken, p)


class Module:
    def __init__(self, hModule, name, path, base, size, pid):
        self._hModule = hModule
        self._name = name
        self._base = base
        self._size = size
        self._pid = pid

    @property
    def name(self):
        return self._name

    @property
    def addr_info(self):
        return self._base, self._size

    @property
    def pid(self):
        return self._pid

    @property
    def tid(self):
        return self._tid

    @property
    def path(self):
        return self._path


class Thread:
    def __init__(self, tid, pid, flags=0):
        self._tid = tid
        self._pid = pid
        self._flags = flags
        self._handle = None

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    @property
    def token(self):
        raise NotImplementedError()


class Process:
    def __init__(self, pid, name=None, parent_pid=0, flags=0):
        self._pid = pid
        self._name = ""
        if name:
            self._name = name.decode('utf-8')
        self._parent_pid = parent_pid
        self._flags = flags
        self._handle = None

    @property
    def name(self):
        if not self._name:
            try:
                handle = self.open()
                self._name = Kernel32.GetProcessImageFileNameW(handle)
            except:
                self._name = ""
        return self._name

    @property
    def pid(self):
        return self._pid

    @property
    def parent_pid(self):
        if not self._parent_pid:
            # Get the parent pid
            pass
        return self._parent_pid

    def open(self, access=ProcessAccessRights.PROCESS_QUERY_INFORMATION):
        # We can't open if we're pid 0 or 4
        if not self._handle:
            self._handle = Kernel32.OpenProcess(self._pid, access)
        return self._handle

    def close(self):
        if self._handle:
            tmp = self._handle
            self._handle = None
            Kernel32.CloseHandle(tmp)

    def __str__(self):
        proc = namedtuple('Process', ['pid', 'name', 'parent_pid'])
        return str(proc(self.pid, self.name, self.parent_pid))

    def get_token(self, access=TokenPrivileges.TOKEN_QUERY):
        hProc = self.open()
        hToken = Advapi32.OpenProcessToken(hProc, access)
        return Token(hToken)

    @property
    def modules(self):
        snap = Kernel32.CreateToolhelp32Snapshot(Toolhelp32Flags.TH32CS_SNAPMODULE, self._pid)
        module = Kernel32.Module32First(snap)
        yield Module(module['hModule'],
                     module['szModule'],
                     module['szExePath'],
                     module['modBaseAddr'],
                     module['modBaseSize'],
                     module['th32ProcessID'])
        while True:
            try:
                module = Kernel32.Module32Next(snap)
                yield Module(module['hModule'],
                             module['szModule'],
                             module['szExePath'],
                             module['modBaseAddr'],
                             module['modBaseSize'],
                             module['th32ProcessID'])
            except OSError:
                # TODO check for done
                break

    @property
    def threads(self):
        snap = Kernel32.CreateToolhelp32Snapshot(Toolhelp32Flags.TH32CS_SNAPTHREAD, self._pid)
        thread = Kernel32.Thread32First(snap)
        yield Thread(thread['th32ThreadID'],
                     thread['th32OwnerProcessID'],
                     thread['dwFlags'])
        while True:
            try:
                thread = Kernel32.Thread32Next(snap)
                yield Thread(thread['th32ThreadID'],
                             thread['th32OwnerProcessID'],
                             thread['dwFlags'])
            except OSError:
                # TODO check for done
                break


class Snapshot:
    def __init__(self):
        self._hSnapshot = Kernel32.CreateToolhelp32Snapshot(Toolhelp32Flags.TH32CS_SNAPALL)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Kernel32.CloseHandle(self._hSnapshot)

    @property
    def processes(self):
        proc = Kernel32.Process32First(self._hSnapshot)
        yield Process(proc['th32ProcessID'],
                      name=proc['szExeFile'],
                      parent_pid=proc['th32ParentProcessID'],
                      flags=proc['dwFlags'])
        while True:
            try:
                proc = Kernel32.Process32Next(self._hSnapshot)
                yield Process(proc['th32ProcessID'],
                              name=proc['szExeFile'],
                              parent_pid=proc['th32ParentProcessID'],
                              flags=proc['dwFlags'])
            except OSError:
                # TODO check for done
                break


def find_user_processes(username):
    """Find a process owned by user `username`"""
    with Snapshot() as snap:
        for proc in snap.processes:
            if proc.pid == 0 or proc.pid == 4:
                continue
            #print(str(proc))
            yield proc
            # yield str(proc.name), proc.pid
            #token = proc.get_token()
            #if token.user.lower() == username.lower():
            #    yield proc.name, proc.pid


def get_effective_token():
    hToken = None
    try:
        hThread = windll.kernel32.GetCurrentThread()
        hToken = Advapi32.OpenThreadToken(hThread, TokenPrivileges.TOKEN_QUERY)
    except OSError:
        # XXX Make sure error was that token doesn't exist
        pass

    if not hToken:
        # if that fails, try the process token.  Caller handles this exception
        hProc = windll.kernel32.GetCurrentProcess()
        hToken = Advapi32.OpenProcessToken(hProc, TokenPrivileges.TOKEN_QUERY)

    return Token(hToken)


def whoami():
    """Return (username, sid) for the current thread's user"""
    # Try the thread token
    token = get_effective_token()
    return token.user
