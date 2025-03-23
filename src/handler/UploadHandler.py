import pathlib
import os
import stat
import hashlib

from api.BDNetdisk import create_file, create_upload_task, get_upload_domains, upload_file_block
from error import InvalidStateError
from context import Context
from util import PathUtil

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