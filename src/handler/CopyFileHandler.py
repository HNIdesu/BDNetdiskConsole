
import re

from context import Context
from error import InvalidStateError, IllegalOperationError,ArgumentError
from util import PathUtil
from api import errno as ERRNO
from api.BDNetdisk import copy_files, get_file_list

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    file_collection = list()
    dest_directory = PathUtil.get_absolute_remote_path(context.current_directory,args.dest_directory)
    if args.regex:
        source_path = PathUtil.get_absolute_remote_path(context.current_directory,args.source_path)
        if source_path == "/":
            raise IllegalOperationError("禁止复制根目录")
        parent_dir = PathUtil.resolve(source_path,"..")
        pattern = source_path[source_path.rfind("/")+1:]
        start = 0
        while True:
            file_list = get_file_list(context,start,1000,parent_dir)
            for file in file_list:
                if re.match(pattern,file["server_filename"]):
                    file_path = file["path"]
                    if args.name:
                        name = args.name
                    else:
                        name = file_path[file_path.rfind("/")+1:]
                    if context.current_directory.startswith(file_path):
                        raise IllegalOperationError("禁止复制当前目录及其父目录")
                    file_collection.append((file_path,dest_directory,name,None))
            if len(file_list) == 0:break
            start += len(file_list)
    else:
        try:
            source_path = PathUtil.get_absolute_remote_path(context.current_directory,args.source_path)
        except Exception:
            raise ArgumentError("输入路径无效")
        if source_path == "/":
            raise IllegalOperationError("禁止复制根目录")
        if context.current_directory.startswith(source_path):
            raise IllegalOperationError("禁止复制当前目录及其父目录")
        if args.name:
            name = args.name
        else:
            name = source_path[source_path.rfind("/")+1:]
        file_collection.append((source_path,dest_directory,name,None))
    if args.dry_run:
        for file in file_collection:
            print(f"{file[0]} ->  {PathUtil.resolve(file[1],file[2])}")
    else:
        response = copy_files(context,file_collection,0,ondup=args.ondup)
        for result in response["info"]:
            if result["errno"] != ERRNO.OK:
                print(f"复制 {result["path"]} 失败，错误码：{result["errno"]}")