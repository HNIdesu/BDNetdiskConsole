from api.BDNetdisk import search_files
from context import Context
from error import InvalidStateError,ArgumentError
from util import PathUtil

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    try:
        remote_directory = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_directory)
    except Exception:
        raise ArgumentError("输入路径无效")
    for file in search_files(context,remote_directory,args.name,args.recurse):
        print(file["path"])