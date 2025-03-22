import json as JSON
import re

from urllib.parse import urlencode
from urllib.request import urlopen
from context import Context
from error import ErrnoError, InvalidStateError, IllegalOperationError
from error.ArgumentError import ArgumentError
from handler import ListFileHandler
from util import PathUtil
from api import errno as ERRNO

def remove_files(context:Context,filelist:list,_async:int) -> any:
    host = "pan.baidu.com"
    path = "/rest/2.0/xpan/file"
    request_body = urlencode({
        "filelist":JSON.dumps(filelist),
        "async":_async
    }).encode("utf-8")
    with urlopen(f"https://{host}{path}?"+urlencode({
        "method":"filemanager",
        "access_token":context.access_token,
        "opera":"delete"
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json
    
def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    file_collection = list()
    if args.regex:
        remote_path = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_paths[0])
        if remote_path == "/":
            raise IllegalOperationError("禁止删除根目录")
        parent_dir = PathUtil.resolve(remote_path,"..")
        pattern = remote_path[remote_path.rfind("/")+1:]
        start = 0
        while True:
            file_list = ListFileHandler.get_file_list(context,start,1000,parent_dir)
            for file in file_list:
                if re.match(pattern,file["server_filename"]):
                    file_path = file["path"]
                    if context.current_directory.startswith(file_path):
                        raise IllegalOperationError("禁止删除当前目录及其父目录")
                    file_collection.append(file_path)
            if len(file_list) == 0: break
            start += len(file_list)
    else:
        for remote_path in args.remote_paths:
            try:
                remote_path = PathUtil.get_absolute_remote_path(context.current_directory,remote_path)
            except Exception:
                raise ArgumentError("输入路径无效")
            if remote_path == "/":
                raise IllegalOperationError("禁止删除根目录")
            if context.current_directory.startswith(remote_path):
                raise IllegalOperationError("禁止删除当前目录及其父目录")
            file_collection.append(remote_path)
    if args.dry_run:
        for file in file_collection:
            print(file)
    else:
        response = remove_files(context,file_collection,0)
        for result in response["info"]:
            if result["errno"] != ERRNO.OK:
                print(f"删除 {result["path"]} 失败，错误码：{result["errno"]}")