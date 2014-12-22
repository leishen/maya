"""
winapi is a module built on ctypeshelper.  It is meant to be an easy-to-use implementation of
as many Windows calls as are completed, focusing initially on the Security APIs (advapi32) and
the Windows system calls (ntdll).  The module should make Windows experimentation significantly
faster, and contains a variety of routines that wrap up common use cases on top of the ctypes
Windows API functions.
"""

__all__ = ['kernel32', 'security', 'registry']
