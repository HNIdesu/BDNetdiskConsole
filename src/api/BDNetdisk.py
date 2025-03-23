from typing import Literal
import json as JSON
import time as TIME
import requests

from context import Context
from urllib.parse import quote, urlencode
from urllib.request import urlopen
from error import *
from api import errno as ERRNO

def copy_files(
    context:Context,
    filelist:list[(str,str,str,str)],
    _async:int,
    ondup:Literal["fail","newcopy","overwrite","skip"]="fail"
    ) -> any:
    if ondup == "overwrite" or ondup == "skip":
        raise NotSupportedError("百度网盘API中尚未实现该功能")
    def foo1(x):
        source_path = x[0]
        result = {"path":source_path,"dest":x[1],"newname":x[2]}
        if x[3]:
            result["ondup"] = x[3]
        return result
    request_body = urlencode({
        "filelist":JSON.dumps(list(map(foo1,filelist))),
        "async":_async,
        "ondup":ondup
    }).encode("utf-8")
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"filemanager",
        "access_token":context.access_token,
        "opera":"copy"
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK and errno != ERRNO.BATCH_TRANSFER_FAILED:
            raise ErrnoError(errno)
        return json


def create_directory(
        context:Context,
        dirpath:str,
        local_ctime:int=-1,
        local_mtime:int=-1
    ):
    if local_ctime == -1:
        local_ctime = int(TIME.time())
    if local_mtime == -1:
        local_mtime = local_ctime
    request_body = urlencode({
        "path":dirpath,
        "isdir":"1",
        "rtype":"0",
        "ctime":local_ctime,
        "mtime":local_mtime,
        "mode":"1"
    }).encode("utf-8")
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"create",
        "access_token":context.access_token,
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        
def get_user_info(context: Context):
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/nas?"+urlencode({
        "method":"uinfo",
        "access_token":context.access_token
    })) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录。")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json

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

def remove_files(context:Context,filelist:list,_async:int) -> any:
    request_body = urlencode({
        "filelist":JSON.dumps(filelist),
        "async":_async
    }).encode("utf-8")
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"filemanager",
        "access_token":context.access_token,
        "opera":"delete"
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json
    
def move_files(
    context:Context,
    filelist:list[(str,str,str,str)],
    _async:int,
    ondup:Literal["fail","newcopy","overwrite","skip"]="fail"
    ) -> any:
    if ondup == "overwrite" or ondup == "skip":
        raise NotSupportedError("百度网盘API中尚未实现该功能")
    def foo1(x):
        source_path = x[0]
        result = {"path":source_path,"dest":x[1],"newname":x[2]}
        if x[3]:
            result["ondup"] = x[3]
        return result
    request_body = urlencode({
        "filelist":JSON.dumps(list(map(foo1,filelist))),
        "async":_async,
        "ondup":ondup
    }).encode("utf-8")
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"filemanager",
        "access_token":context.access_token,
        "opera":"move"
    }),data=request_body) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK and errno != ERRNO.BATCH_TRANSFER_FAILED:
            raise ErrnoError(errno)
        return json

def get_file_list(context:Context,start:int,limit:int,dir:str,folder:int=0)->list:
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode({
        "method":"list",
        "access_token":context.access_token,
        "dir":dir,
        "folder":folder,
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
        return json["list"]
    
def search_files(context:Context,dir:str,key:str,recursion:bool):
    url_args = {
        "method":"search",
        "access_token":context.access_token,
        "dir":dir,
        "key":key
    }
    if recursion:
        url_args["recursion"] = "1"
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/file?"+urlencode(url_args)) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json["list"]
    
def get_file_metas(
    context:Context,
    fsids:list,
    dlink:bool=False,
    thumb:bool=False,
    extra:bool=False,
    need_media:bool=False,
    detail:bool=False):
    url_args = {
        "method":"filemetas",
        "access_token":context.access_token,
        "fsids":fsids
    }
    if dlink:
        url_args["dlink"] = 1
    if thumb:
        url_args["thumb"] = 1
    if extra:
        url_args["extra"] = 1
    if need_media:
        url_args["needmedia"] = 1
    if detail:
        url_args["detail"] = 1
    with urlopen(f"https://pan.baidu.com/rest/2.0/xpan/multimedia?"+urlencode(url_args)) as res:
        json = JSON.loads(res.read().decode("utf-8"))
        errno = json["errno"]
        if errno == ERRNO.ACCESS_TOKEN_VERIFICATION_FAIL:
            context.need_relogin = True
            raise InvalidStateError("登录已过期，请重新登录")
        elif errno != ERRNO.OK:
            raise ErrnoError(errno)
        return json["list"]