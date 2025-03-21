import time
from handler.BaseHandler import BaseHandler
from urllib.request import urlopen
from urllib.parse import urlencode
import json as JSON

from util import PathUtil
from api import errno as ERRNO
from context import Context
from error import ErrnoError,InvalidStateError,ArgumentError

class ListFileHandler(BaseHandler):
    @staticmethod
    def get_absolute_remote_path(curdir:str,remote_directory:str)->str:
        if remote_directory.startswith("/"):
            return remote_directory
        else:
            return PathUtil.resolve(curdir,remote_directory)

    @staticmethod
    def print_file_list(file_list,show_detail=False):
        for file in file_list:
            filename = filename = file.get("server_filename", "")
            if not show_detail:
                print(filename,end="  ")
            else:
                # 获取文件的关键信息
                size = file.get("size", 0)
                server_mtime = file.get("server_mtime", 0)
                path = file.get("path", "")

                # 将修改时间戳转化为可读格式
                server_mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(server_mtime)) if server_mtime else "N/A"
                
                # 如果是目录，大小为空
                if file.get("isdir", 0):
                    size = ""

                # 打印文件的详细信息
                print(f"{server_mtime:<20} {size:>10} {filename}")
            
    def handle(self, context: Context, args):
        if not context.is_logged_in:
            raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录")
        host = "pan.baidu.com"
        path = "/rest/2.0/xpan/file"
        try:
            remote_directory = ListFileHandler.get_absolute_remote_path(context.current_directory,args.remote_directory)
        except Exception:
            raise ArgumentError("输入路径无效")
        if args.all:
            limit = 1000 # 如果显示全部文件，单次请求文件数尽可能大
        else:
            limit = args.limit
        start = args.start
        total_file_count = 0
        while True:
            with urlopen(f"https://{host}{path}?"+urlencode({
                "method":"list",
                "access_token":context.access_token,
                "dir":remote_directory,
                "start":start,
                "limit":limit
            })) as res:
                json = JSON.loads(res.read().decode("utf-8"))
                errno = json["errno"]
                if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
                    context.need_relogin = True
                    raise InvalidStateError("登录已过期，请重新登录")
                elif errno != ERRNO.OK:
                    raise ErrnoError(errno)
                file_list = json["list"]
                total_file_count += len(file_list)
                ListFileHandler.print_file_list(file_list,show_detail=args.detail)
                if (not args.all) or len(file_list)==0:
                    break
                start += limit
        if total_file_count>0 and not args.detail:# 需要手动换行
            print()