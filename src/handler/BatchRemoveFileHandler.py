import os.path as Path
import json as JSON

from context import Context
from error import InvalidStateError
from handler import RemoveFileHandler
from api import errno as ERRNO
from util import PathUtil

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    script_path = args.script_path
    if not Path.exists(script_path):
        raise FileNotFoundError("脚本文件不存在，请检查路径后重试")
    file_collection = list()
    if args.resume and Path.exists("remove_status"):
        with open("remove_status","r",encoding="utf-8") as sr:
            status = JSON.loads(sr.read())
    else:
        status = dict()
    with open(script_path,"r",encoding="utf-8") as sr:
        while True:
            line = sr.readline()
            if line == "": break
            filepath = line.strip()
            if filepath == "": continue
            if not filepath in status:
                file_collection.append(PathUtil.get_absolute_remote_path(context.current_directory,filepath))
            elif status[filepath] != ERRNO.OK:
                file_collection.append(PathUtil.get_absolute_remote_path(context.current_directory,filepath))
    if len(file_collection) > 0:
        response = RemoveFileHandler.remove_files(context,file_collection,0)
        for info in response["info"]:
            status[info["path"]] = info["errno"]
            if info["errno"] != ERRNO.OK:
                print(f"删除 {info["path"]} 失败，错误码：{info["errno"]}")
        with open("remove_status","w",encoding="utf-8") as sw:
            sw.write(JSON.dumps(status))