from urllib.request import urlopen
from urllib.parse import urlencode
import json as JSON

from api import errno as ERRNO
from context import Context
from error import ErrnoError,InvalidStateError

def get_user_info(context: Context):
    host = "pan.baidu.com"
    path = "/rest/2.0/xpan/nas"
    with urlopen(f"https://{host}{path}?"+urlencode({
        "method":"uinfo",
        "access_token":context.access_token
    })) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录。")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录。")
    print(get_user_info(context))