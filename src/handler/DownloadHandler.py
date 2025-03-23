import subprocess
import pathlib

from api.BDNetdisk import get_file_metas
from context import Context
from error import InvalidStateError,ArgumentError
from util import PathUtil,BadUtil

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    try:
        remote_path = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_path)
    except Exception:
        raise ArgumentError("输入路径无效")
    if args.output_path:
        output_path= pathlib.Path(args.output_path).absolute()
    else:
        output_path = pathlib.Path(".",remote_path[remote_path.rfind("/")+1:]).absolute()
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True,exist_ok=True)
    fsid = BadUtil.get_fsid_of_path(context,remote_path)
    fileinfo = get_file_metas(context,[fsid],dlink=True)
    dlink = fileinfo[0]["dlink"]
    subprocess.Popen([
        "curl",
        "-H",
        f"User-Agent: pan.baidu.com",
        "-L",
        f"{dlink}&access_token={context.access_token}",
        "-o",str(output_path)
    ],stdin=subprocess.PIPE,stdout=subprocess.PIPE)