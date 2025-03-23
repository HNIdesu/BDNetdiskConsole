from api.BDNetdisk import get_file_metas
from context import Context
from error import InvalidStateError,ArgumentError
from util import BadUtil, PathUtil
    
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