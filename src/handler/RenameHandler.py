import re

from context import Context
from error import IllegalOperationError, InvalidStateError
from handler import ListFileHandler,MoveFileHandler
from util import PathUtil
from api import errno as ERRNO

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    file_collection = list()
    if args.regex:
        start = 0
        while True:
            file_list = ListFileHandler.get_file_list(context,start,1000,context.current_directory)
            for file in file_list:
                if re.match(args.old_name,file["server_filename"]):
                    file_path = file["path"]
                    new_name = re.sub(args.old_name,args.new_name,file["server_filename"])
                    if context.current_directory.startswith(file_path):
                        raise IllegalOperationError("禁止移动当前目录及其父目录")
                    file_collection.append((file_path,context.current_directory,new_name,None))
            if len(file_list) == 0:break
            start += len(file_list)
    else:
        file_path = PathUtil.get_absolute_remote_path(context.current_directory,args.old_name)
        file_collection.append((file_path,context.current_directory,args.new_name))
    if args.dry_run:
        for file in file_collection:
            print(f"{file[0]} ->  {PathUtil.resolve(file[1],file[2])}")
    else:
        response = MoveFileHandler.move_files(context,file_collection,0)
        for result in response["info"]:
            if result["errno"] != ERRNO.OK:
                print(f"重命名 {result["path"]} 失败，错误码：{result["errno"]}")