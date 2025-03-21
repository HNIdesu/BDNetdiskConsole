import sys
import os.path as Path
from argparse import ArgumentParser
import shlex

src_dir = Path.abspath(Path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from handler import *
from context import Context
context = Context()
print(f"BDNetdisk Console {context.version}")

parser = ArgumentParser()
subparsers = parser.add_subparsers()

login_parser = subparsers.add_parser("login")
login_parser.add_argument("username")
login_parser.set_defaults(handler = LoginHandler)

userinfo_parser = subparsers.add_parser("uinfo")
userinfo_parser.set_defaults(handler = UserInfoHandler)

while True:
    cmd = input(context.prompt)
    cmd = cmd.strip()
    if cmd == "":
        continue
    if cmd == "help":
        parser.print_help()
    elif cmd == "version":
        print(context.version)
    elif cmd == "quit":
        raise SystemExit(0)
    else:
        try:
            args = parser.parse_args(shlex.split(cmd))
            args.handler().handle(context,args)
        except SystemExit:
            pass
        except Exception as ex:
            print(ex)