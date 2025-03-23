from context import Context
from error import ErrnoError, InvalidStateError
from api import errno as ERRNO
from error.ArgumentError import ArgumentError
from util import PathUtil
from api.BDNetdisk import create_directory
            
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