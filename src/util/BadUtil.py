from api.BDNetdisk import get_file_list, search_files
from context import Context
from error import IllegalOperationError,NotSupportedError
from util import PathUtil

def get_fsid_of_path(context: Context,remote_file:str)->int:
    if remote_file == "/":
        raise IllegalOperationError("不是一个文件")
    parent_dir = PathUtil.resolve(remote_file,"..")
    file_name = remote_file[remote_file.rfind("/")+1:]
    file_list = get_file_list(context,0,1000,parent_dir)
    search_result = next((item for item in file_list if item["server_filename"] == file_name), None)
    if not search_result:
        raise FileNotFoundError("文件不存在")
    elif search_result["isdir"] == 1:
        raise IllegalOperationError("不是一个文件")
    return search_result["fs_id"]

def get_file_info(context: Context,remote_path:str):
    if remote_path == "/":
        raise NotSupportedError("无法获取根目录信息")
    parent_dir = PathUtil.resolve(remote_path,"..")
    filename = remote_path[remote_path.rfind("/")+1:]
    for file in search_files(context,parent_dir,filename,False):
        if file["path"] == remote_path:
            return file
    raise FileNotFoundError("文件或目录不存在")