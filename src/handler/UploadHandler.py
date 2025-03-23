from urllib.request import urlopen
from urllib.parse import urlencode,quote
import json as JSON
import time as TIME
import pathlib
import os
import stat
import hashlib
import requests

from api import errno as ERRNO
from error import ErrnoError, InvalidStateError
from context import Context
from util import PathUtil

def get_upload_domains(context:Context,path:str,uploadid:str)->any:
    with urlopen(f"https://d.pcs.baidu.com/rest/2.0/pcs/file?"+urlencode({
        "method":"locateupload",
        "appid":"250528",
        "access_token":context.access_token,
        "path":path,
        "uploadid":uploadid,
        "upload_version":"2.0"
    })) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["error_code"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json

def create_upload_task(
        context:Context,
        path:str,
        size:int,
        isdir:int,
        blocklist:list,
    ) -> any:
    request_body = urlencode({
        "path":quote(path),
        "size":size,
        "isdir":isdir,
        "block_list":JSON.dumps(blocklist),
        "autoinit":1
    })
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"precreate",
        "access_token":context.access_token
    }),data=request_body.encode()) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json

def upload_file_block(context:Context,path:str,upload_id:str,partseq:int,data:bytes,domain:str=None):
    if domain == None:
        domain = get_upload_domains(context,path,upload_id)["servers"][0]
    url = f"{domain}/rest/2.0/pcs/superfile2?"+urlencode({
            "method":"upload",
            "access_token":context.access_token,
            "type":"tmpfile",
            "path":path,
            "uploadid":upload_id,
            "partseq":partseq
        })
    files = {
        'file': ('filename.txt', data, 'application/octet-stream')
    }
    with requests.request("POST",url,files = files) as res:
        json = res.json()
        if "error_code" in json:
            errno = json["error_code"]
            if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
                context.need_relogin = True
                raise InvalidStateError("登录已过期，请重新登录")
            elif errno != ERRNO.OK:
                raise ErrnoError(errno)
        return json

class FileBlock:
    def __init__(self,filepath:str,start:int,size:int,md5:str):
        self.filepath = filepath
        self.start = start
        self.size = size
        self.md5 = md5
    def read_all_bytes(self)->bytes:
        with open(self.filepath,"br") as br:
            br.seek(self.start,0)
            return br.read(self.size)

def generate_file_blocks(path:str,max_block_size:int=4*1024*1024):
    filesize = os.stat(path).st_size
    with open(path,"br") as br:
        for start in range(0,filesize,max_block_size):
            block_data = br.read(max_block_size)
            md5 = hashlib.md5(block_data).hexdigest()
            yield FileBlock(path,start,len(block_data),md5)

def create_file(
    context: Context,
    path:str,
    size:int,
    isdir:int,
    blocklist:list,
    uploadid:str,
    rtype:int,
    local_ctime:int=-1,
    local_mtime:int=-1
    ):
    if local_ctime == -1:
        local_ctime = int(TIME.time())
    if local_mtime == -1:
        local_mtime = local_ctime
    request_body = urlencode({
        "path":path,
        "size":size,
        "isdir":int,
        "rtype":rtype,
        "local_ctime":local_ctime,
        "local_mtime":local_mtime,
        "block_list":JSON.dumps(blocklist),
        "uploadid":uploadid,
        "isdir":isdir
    })
    with urlopen("https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"create",
        "access_token":context.access_token,
    }),data=request_body.encode("utf-8")) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录。")
    file_path = args.local_path
    file_info = os.stat(file_path)
    if args.name:
        name = args.name
    else:
        name = pathlib.Path(file_path).name
    remote_dest_path = PathUtil.resolve(context.current_directory,args.remote_directory,name)
    if stat.S_ISDIR(file_info.st_mode):
        raise NotImplementedError("暂未实现上传目录功能")
    else:
        isdir = 0
        size = file_info.st_size
        file_block_list = list(generate_file_blocks(file_path))
        block_list = list(map(lambda x:x.md5,file_block_list))
    response = create_upload_task(
        context,
        remote_dest_path,
        size,
        isdir,
        block_list
    )
    upload_id = response["uploadid"]
    blocks_to_upload = list(map(lambda x:(x,file_block_list[x]),response["block_list"]))
    upload_domains = list(
        filter(
            lambda x:x.startswith("https"),
            map(
                lambda x:x["server"],
                get_upload_domains(context,remote_dest_path,upload_id)["servers"]
            )
        )
    )
    uploaded_block_count = 0
    for index, block in blocks_to_upload:
        print(f"\r正在上传 {uploaded_block_count}/{len(blocks_to_upload)} 分块",end="")
        upload_file_block(context,remote_dest_path,upload_id,index,block.read_all_bytes(),upload_domains[0])
        uploaded_block_count += 1
    print("\r" + " " * 50,end="")
    print("\r正在创建文件...",end="")
    create_file(
        context,
        remote_dest_path,
        size,
        isdir,
        block_list,
        upload_id,
        2,
        local_ctime=int(file_info.st_birthtime),
        local_mtime=int(file_info.st_mtime)
    )
    print("\r" + " " * 50,end="\r")