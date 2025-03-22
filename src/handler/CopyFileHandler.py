import json as JSON
import re
from typing import Literal

from urllib.parse import urlencode
from urllib.request import urlopen
from context import Context
from error import ErrnoError, InvalidStateError, IllegalOperationError,NotSupportedError,ArgumentError
from handler import ListFileHandler
from util import PathUtil
from api import errno as ERRNO

def copy_files(
    context:Context,
    filelist:list[(str,str,str,str)],
    _async:int,
    ondup:Literal["fail","newcopy","overwrite","skip"]="fail"
    ) -> any:
    host = "pan.baidu.com"
    path = "/rest/2.0/xpan/file"
    if ondup == "overwrite" or ondup == "skip":
        raise NotSupportedError("百度网盘API中尚未实现该功能")
    def foo1(x):
        source_path = x[0]
        result = {"path":source_path,"dest":x[1],"newname":x[2]}
        if x[3]:
            result["ondup"] = x[3]
        return result
    request_body = urlencode({
        "filelist":JSON.dumps(list(map(foo1,filelist))),
        "async":_async,
        "ondup":ondup
    }).encode("utf-8")
    with urlopen(f"https://{host}{path}?"+urlencode({
        "method":"filemanager",
        "access_token":context.access_token,
        "opera":"copy"
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK and errno != ERRNO.BATCH_TRANSFER_FAILED:
            raise ErrnoError(errno)
        return json

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
            file_list = ListFileHandler.get_file_list(context,start,1000,parent_dir)
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