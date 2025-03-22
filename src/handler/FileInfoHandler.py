from urllib.parse import urlencode
from urllib.request import urlopen
import json as JSON

from context import Context
from error import ErrnoError, InvalidStateError
from error.ArgumentError import ArgumentError
from api import errno as ERRNO
from util import BadUtil, PathUtil

def get_file_metas(
    context:Context,
    fsids:list,
    dlink:bool=False,
    thumb:bool=False,
    extra:bool=False,
    need_media:bool=False,
    detail:bool=False):
    host = "pan.baidu.com"
    path = "/rest/2.0/xpan/multimedia"
    url_args = {
        "method":"filemetas",
        "access_token":context.access_token,
        "fsids":fsids
    }
    if dlink:
        url_args["dlink"] = 1
    if thumb:
        url_args["thumb"] = 1
    if extra:
        url_args["extra"] = 1
    if need_media:
        url_args["needmedia"] = 1
    if detail:
        url_args["detail"] = 1
    with urlopen(f"https://{host}{path}?"+urlencode(url_args)) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json["list"]
    
def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    try:
        remote_file = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_file)
    except Exception:
        raise ArgumentError("输入路径无效")
    fs_id = BadUtil.get_fsid_of_path(context,remote_file)
    print(
        get_file_metas(context,[fs_id],args.dlink,args.thumb,args.extra,args.media,args.detail)[0]
    )