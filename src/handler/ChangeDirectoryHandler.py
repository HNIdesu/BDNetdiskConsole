from context import Context
from error import InvalidStateError,IllegalOperationError, ArgumentError
from util import BadUtil, PathUtil

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    try:
        remote_directory = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_directory)
    except Exception:
        raise ArgumentError("输入路径无效")
    if remote_directory == "/":
        context.current_directory = "/"
    else:
        try:
            dirinfo = BadUtil.get_file_info(context,remote_directory)
            if dirinfo["isdir"] == 1:
                context.current_directory = remote_directory
            else:
                raise IllegalOperationError("不是一个目录")
        except FileNotFoundError:
            raise FileNotFoundError("目录不存在")
    