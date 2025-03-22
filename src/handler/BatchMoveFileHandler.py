import os.path as Path
import json as JSON
import shlex
from argparse import ArgumentParser

from handler import MoveFileHandler
from util import PathUtil
from context import Context
from error import InvalidStateError,IllegalOperationError
from api import errno as ERRNO

status_file_path = "move_status"
def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    script_path = args.script_path
    if args.resume and Path.exists(status_file_path):
        with open(status_file_path,"r",encoding="utf-8") as sr:
            status = JSON.loads(sr.read())
    else:
        status = {}
    if not Path.exists(script_path):
        raise FileNotFoundError("脚本文件不存在，请检查路径后重试")
    file_collection = list()
    parser = ArgumentParser()
    parser.add_argument("source_path")
    parser.add_argument("dest_directory")
    parser.add_argument("--name")
    parser.add_argument("--ondup",default="fail")
    with open(script_path,"r",encoding="utf-8") as sr:
        while True:
            line = sr.readline()
            if line == "": break
            line = line.strip()
            if line == "": continue
            line_args = parser.parse_args(shlex.split(line))
            source_path = PathUtil.get_absolute_remote_path(context.current_directory,line_args.source_path)
            dest_directory = PathUtil.get_absolute_remote_path(context.current_directory,line_args.dest_directory)
            if source_path == "/":
                raise IllegalOperationError("禁止移动根目录")
            if context.current_directory.startswith(source_path):
                raise IllegalOperationError("禁止移动当前目录及其父目录")
            if line_args.name:
                name = line_args.name
            else:
                name = source_path[source_path.rfind("/")+1:]
            if source_path in status:
                if status[source_path] != 0:
                    file_collection.append((source_path,dest_directory,name,line_args.ondup))
            else:
                file_collection.append((source_path,dest_directory,name,line_args.ondup))
    chunk_size = 50
    transfered_file_count = 0
    for i in range(0, len(file_collection), chunk_size):
        print(f"正在移动文件: {i}/{len(file_collection)}")
        response = MoveFileHandler.move_files(context,file_collection[i:i+chunk_size],0,args.ondup)
        for info in response["info"]:
            status[info["path"]] = info["errno"]
            if info["errno"] != ERRNO.OK:
                print(f"移动 {info["path"]} 失败，错误码：{info["errno"]}")
            else:
                transfered_file_count += 1
        with open(status_file_path,"w",encoding="utf-8") as sw:
            sw.write(JSON.dumps(status))
    print(f"本次移动了{transfered_file_count}/{len(file_collection)}个文件")