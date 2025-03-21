from urllib.parse import urlencode
from urllib.request import urlopen
import json as JSON

from context import Context
from error import ErrnoError, InvalidStateError
from error.ArgumentError import ArgumentError
from handler.BaseHandler import BaseHandler
from util import PathUtil
from api import errno as ERRNO

class FileInfoHandler(BaseHandler):
    def get_absolute_remote_path(curdir:str,remote_directory:str)->str:
        if remote_directory.startswith("/"):
            return remote_directory
        else:
            return PathUtil.resolve(curdir,remote_directory)
    @staticmethod
    def get_fs_id(remote_file:str,context: Context) ->int:
        if remote_file == "/":
            raise ArgumentError("不是一个文件")
        parent_dir = PathUtil.resolve(remote_file,"..")
        file_name = remote_file[remote_file.rfind("/")+1:]
        host = "pan.baidu.com"
        path = "/rest/2.0/xpan/file"
        with urlopen(f"https://{host}{path}?"+urlencode({
            "method":"search",
            "access_token":context.access_token,
            "dir":parent_dir,
            "key":file_name,
        })) as res:
            json = JSON.loads(res.read().decode("utf-8"))
            errno = json["errno"]
            if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
                context.need_relogin = True
                raise InvalidStateError("登录已过期，请重新登录")
            elif errno != ERRNO.OK:
                raise ErrnoError(errno)
            search_result = next((item for item in json["list"] if item["server_filename"] == file_name), None)
            if not search_result:
                raise FileNotFoundError("文件不存在")
            elif search_result["isdir"] == 1:
                raise ArgumentError("不是一个文件")
            return search_result["fs_id"]
        
    def handle(self, context: Context, args):
        if not context.is_logged_in:
            raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
        try:
            remote_file = FileInfoHandler.get_absolute_remote_path(context.current_directory,args.remote_file)
        except Exception:
            raise ArgumentError("输入路径无效")
        fs_id = FileInfoHandler.get_fs_id(remote_file,context)
        host = "pan.baidu.com"
        path = "/rest/2.0/xpan/multimedia"
        url_args = {
            "method":"filemetas",
            "access_token":context.access_token,
            "fsids":[fs_id]
        }
        if args.dlink:
            url_args["dlink"] = 1
        if args.thumb:
            url_args["thumb"] = 1
        if args.extra:
            url_args["extra"] = 1
        if args.media:
            url_args["needmedia"] = 1
        if args.detail:
            url_args["detail"] = 1
        with urlopen(f"https://{host}{path}?"+urlencode(url_args)) as res:
            json = JSON.loads(res.read().decode("utf-8"))
            errno = json["errno"]
            if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
                context.need_relogin = True
                raise InvalidStateError("登录已过期，请重新登录")
            elif errno != ERRNO.OK:
                raise ErrnoError(errno)
            print(json)