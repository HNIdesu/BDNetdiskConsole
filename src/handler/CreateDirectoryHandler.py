import time as TIME
from urllib.parse import urlencode
from urllib.request import urlopen
import json as JSON

from context import Context
from error import ErrnoError, InvalidStateError
from api import errno as ERRNO
from error.ArgumentError import ArgumentError
from util import PathUtil

def create_directory(
        context:Context,
        dirpath:str,
        local_ctime:int=-1,
        local_mtime:int=-1
    ):
    if local_ctime == -1:
        local_ctime = int(TIME.time())
    if local_mtime == -1:
        local_mtime = local_ctime
    request_body = urlencode({
        "path":dirpath,
        "isdir":"1",
        "rtype":"0",
        "ctime":local_ctime,
        "mtime":local_mtime,
        "mode":"1"
    }).encode("utf-8")
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"create",
        "access_token":context.access_token,
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
            
def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    try:
        remote_directory = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_directory)
    except Exception:
        raise ArgumentError("输入路径无效")
    try:
        create_directory(context,remote_directory)
    except ErrnoError as ex:
        if ex.errno == ERRNO.FILE_ALREADY_EXISTS:
            if not args.force:
                raise FileExistsError("目录已存在")
        else:
            raise ex