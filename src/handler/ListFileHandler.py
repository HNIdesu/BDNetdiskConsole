import time

from api.BDNetdisk import get_file_list
from context import Context
from error import InvalidStateError,ArgumentError
from util import PathUtil

def print_file_list(file_list,show_detail=False):
    for file in file_list:
        filename = filename = file.get("server_filename", "")
        if not show_detail:
            print(filename,end="  ")
        else:
            # 获取文件的关键信息
            size = file.get("size", 0)
            server_mtime = file.get("server_mtime", 0)
            # 将修改时间戳转化为可读格式
            server_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(server_mtime)) if server_mtime else "N/A"
            
            # 如果是目录，大小为空
            if file.get("isdir", 0):
                size = ""
            # 打印文件的详细信息
            print(f"{server_mtime:<20} {size:>10} {filename}")
    
def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
    try:
        remote_directory = PathUtil.get_absolute_remote_path(context.current_directory,args.remote_directory)
    except Exception:
        raise ArgumentError("输入路径无效")
    if args.all:
        limit = 1000 # 如果显示全部文件，单次请求文件数尽可能大
    else:
        limit = args.limit
    start = args.start
    total_file_count = 0
    while True:
        file_list = get_file_list(context,start,limit,remote_directory)
        total_file_count += len(file_list)
        print_file_list(file_list,show_detail=args.detail)
        if (not args.all) or len(file_list)==0:
            break
        start += limit
    if total_file_count>0 and not args.detail:# 需要手动换行
        print()