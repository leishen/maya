#!/usr/bin/env python3


def enable_all_privileges_example():
    from maya.winutils.osinfo import whoami, get_effective_token, TokenPrivileges

    print(whoami())
    token = get_effective_token(access=TokenPrivileges.TOKEN_QUERY | TokenPrivileges.TOKEN_ADJUST_PRIVILEGES)
    print(token)
    for priv in token.privileges:
        print("Enabling {0}".format(priv.name))
        token.enable_privilege(priv)
    print(list(token.privileges))


if __name__ == "__main__":
    enable_all_privileges_example()
