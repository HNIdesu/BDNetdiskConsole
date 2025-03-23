import sys
import os.path as Path
from argparse import ArgumentParser
import shlex

src_dir = Path.abspath(Path.dirname(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from handler import LoginHandler,ListFileHandler,UserInfoHandler,ListUserHandler,CreateDirectoryHandler,ChangeDirectoryHandler,FileInfoHandler,FindFileHandler,RemoveFileHandler,BatchRemoveFileHandler,CopyFileHandler,MoveFileHandler,BatchCopyFileHandler,BatchMoveFileHandler,RenameHandler
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

remove_file_parser = subparsers.add_parser("rm")
remove_file_parser.add_argument("remote_paths",type=str,nargs="+")
remove_file_parser.add_argument("--regex",required=False,action="store_true",help="使用正则匹配文件名，如果启用该选项，只会删除第一个表达式匹配到的文件")
remove_file_parser.add_argument("--dry-run",required=False,action="store_true",help="只输出要删除的文件但是不执行删除操作")
remove_file_parser.set_defaults(handler = RemoveFileHandler)

batch_remove_file_parser = subparsers.add_parser("rmx")
batch_remove_file_parser.add_argument("script_path",type=str)
batch_remove_file_parser.add_argument("--resume",required=False,action="store_true",help="重试失败的任务")
batch_remove_file_parser.set_defaults(handler = BatchRemoveFileHandler)

copy_file_parser = subparsers.add_parser("cp")
copy_file_parser.add_argument("source_path",type=str)
copy_file_parser.add_argument("dest_directory",type=str)
copy_file_parser.add_argument("--name",required=False,type=str,help="如果需要重命名文件，可以设置该参数")
copy_file_parser.add_argument("--regex",required=False,action="store_true",help="使用正则匹配源文件名")
copy_file_parser.add_argument("--ondup",required=False,default="fail",type=str,help="目标文件已存在时的处理方法")
copy_file_parser.add_argument("--dry-run",required=False,action="store_true",help="只输出要复制的文件和目标文件但是不执行复制操作")
copy_file_parser.set_defaults(handler = CopyFileHandler)

batch_copy_file_parser = subparsers.add_parser("cpx")
batch_copy_file_parser.add_argument("script_path",type=str)
batch_copy_file_parser.add_argument("--ondup",required=False,default="fail",type=str,help="目标文件已存在时的处理方法")
batch_copy_file_parser.add_argument("--resume",required=False,action="store_true",help="重试失败的任务")
batch_copy_file_parser.set_defaults(handler = BatchCopyFileHandler)

move_file_parser = subparsers.add_parser("mv")
move_file_parser.add_argument("source_path",type=str)
move_file_parser.add_argument("dest_directory",type=str)
move_file_parser.add_argument("--name",required=False,type=str,help="如果需要重命名文件，可以设置该参数")
move_file_parser.add_argument("--regex",required=False,action="store_true",help="使用正则匹配源文件名")
move_file_parser.add_argument("--ondup",required=False,default="fail",type=str,help="目标文件已存在时的处理方法")
move_file_parser.add_argument("--dry-run",required=False,action="store_true",help="只输出要移动的文件和目标文件但是不执行移动操作")
move_file_parser.set_defaults(handler = MoveFileHandler)

batch_move_file_parser = subparsers.add_parser("mvx")
batch_move_file_parser.add_argument("script_path",type=str)
batch_move_file_parser.add_argument("--ondup",required=False,default="fail",type=str,help="目标文件已存在时的处理方法")
batch_move_file_parser.add_argument("--resume",required=False,action="store_true",help="重试失败的任务")
batch_move_file_parser.set_defaults(handler = BatchMoveFileHandler)

rename_parser = subparsers.add_parser("rename")
rename_parser.add_argument("--regex",required=False,action="store_true",help="使用正则匹配源文件名")
rename_parser.add_argument("--dry-run",required=False,action="store_true",help="只输出要重命名的文件和目标文件但是不执行重命名操作")
rename_parser.add_argument("old_name",type=str)
rename_parser.add_argument("new_name",type=str)
rename_parser.set_defaults(handler = RenameHandler)

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