#!/usr/bin/env python3


def print_process_modules_example():
    from maya.winutils.osinfo import Snapshot
    with Snapshot() as snap:
        for proc in snap.processes:
            try:
                print(proc)
                for mod in proc.modules:
                    print("    {0}".format(mod))
            except OSError as e:
                if e.winerror == 6:     # Invalid handle
                    continue
                else:
                    raise


def find_processes_example():
    from maya.winutils.osinfo import whoami, find_user_processes
    user = whoami()
    print(user)
    for proc in find_user_processes(user.name):
        print(proc)



if __name__ == "__main__":
    print_process_modules_example()
    find_processes_example()
