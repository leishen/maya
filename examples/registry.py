#!/usr/bin/env python3

def registry_example():
    from maya.winutils.registry import RegKey
    import winreg
    with RegKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control") as key:
        for item in key:
            print(item)

if __name__ == "__main__":
    registry_example()