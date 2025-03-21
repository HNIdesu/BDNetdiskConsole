import time
from urllib.parse import urlencode
from urllib.request import urlopen
import json as JSON

from context import Context
from error import ErrnoError, InvalidStateError, InvalidOperationError
from api import errno as ERRNO
from error.ArgumentError import ArgumentError
from handler.BaseHandler import BaseHandler
from util import PathUtil

class CreateDirectoryHandler(BaseHandler):
    @staticmethod
    def get_absolute_remote_path(curdir:str,remote_directory:str)->str:
        if remote_directory.startswith("/"):
            return remote_directory
        else:
            return PathUtil.resolve(curdir,remote_directory)
    def handle(self, context: Context, args):
        if not context.is_logged_in:
            raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
        host = "pan.baidu.com"
        path = "/rest/2.0/xpan/file"
        try:
            remote_directory = CreateDirectoryHandler.get_absolute_remote_path(context.current_directory,args.remote_directory)
        except Exception:
            raise ArgumentError("输入路径无效")
        request_body = urlencode({
            "path":remote_directory,
            "isdir":"1",
            "rtype":"0",
            "ctime":int(time.time()),
            "mtime":int(time.time()),
            "mode":"1"
        }).encode("utf-8")
        with urlopen(f"https://{host}{path}?"+urlencode({
                "method":"create",
                "access_token":context.access_token,
            }),data=request_body) as res:
                json = JSON.loads(res.read().decode("utf-8"))
                errno = json["errno"]
                if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
                    context.need_relogin = True
                    raise InvalidStateError("登录已过期，请重新登录")
                elif errno == ERRNO.FILE_ALREADY_EXISTS:
                    if not args.force:
                        raise InvalidOperationError("文件已存在")
                elif errno != ERRNO.OK:
                    raise ErrnoError(errno)