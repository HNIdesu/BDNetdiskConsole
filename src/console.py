import sys
import os.path as Path
from argparse import ArgumentParser
import shlex

src_dir = Path.abspath(Path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from handler import LoginHandler,ListFileHandler,UserInfoHandler,ListUserHandler,CreateDirectoryHandler,ChangeDirectoryHandler,FileInfoHandler,FindFileHandler
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

list_user_parser = subparsers.add_parser("listusers")
list_user_parser.set_defaults(handler = ListUserHandler)

list_file_parser = subparsers.add_parser("ls")
list_file_parser.add_argument("remote_directory",type=str)
list_file_parser.add_argument("--start",required=False,default=0,type=int)
list_file_parser.add_argument("--limit",required=False,default=50,type=int)
list_file_parser.add_argument("--detail",required=False,action="store_true")
list_file_parser.add_argument("--all",required=False,action="store_true")
list_file_parser.set_defaults(handler = ListFileHandler)

mkdir_parser = subparsers.add_parser("mkdir")
mkdir_parser.add_argument("remote_directory",type=str)
mkdir_parser.add_argument("--force",required=False,action="store_true")
mkdir_parser.set_defaults(handler = CreateDirectoryHandler)

change_directory_parser = subparsers.add_parser("cd")
change_directory_parser.add_argument("remote_directory",type=str)
change_directory_parser.set_defaults(handler = ChangeDirectoryHandler)

find_file_parser = subparsers.add_parser("find")
find_file_parser.add_argument("remote_directory",type=str)
find_file_parser.add_argument("--name",required=False,type=str)
find_file_parser.add_argument("--recurse",required=False,action="store_true")
find_file_parser.set_defaults(handler = FindFileHandler)

file_info_parser = subparsers.add_parser("file")
file_info_parser.add_argument("remote_file",type=str)
file_info_parser.add_argument("--dlink",required=False,action="store_true")
file_info_parser.add_argument("--detail",required=False,action="store_true")
file_info_parser.add_argument("--thumb",required=False,action="store_true")
file_info_parser.add_argument("--media",required=False,action="store_true")
file_info_parser.add_argument("--extra",required=False,action="store_true")
file_info_parser.set_defaults(handler = FileInfoHandler)

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
            args.handler.handle(context,args)
        except SystemExit:
            pass
        except Exception as ex:
            print(ex)