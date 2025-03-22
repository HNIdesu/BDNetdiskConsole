from urllib.parse import urlencode,urlparse,parse_qs
import time
from context import Context
from manager import AppPrefManager,UserManager

def login_guide(username:str,context:Context):
    app_key = AppPrefManager.get_app_key()
    if not app_key:
        raise KeyError("app_key 未设置，请检查配置")
    host = "openapi.baidu.com"
    path = "/oauth/2.0/authorize"
    auth_url = f"https://{host}{path}?"+urlencode({
        "response_type":"token",
        "redirect_uri":"oob",
        "scope":"basic,netdisk",
        "client_id":app_key
    })
    print("请登录以下网址获取授权码：")
    print(auth_url)
    redirect_url = input("登录成功后，请复制浏览器地址栏的完整 URL 并粘贴到这里：\n")

    parsed_url = urlparse(redirect_url)
    fragment = parsed_url.fragment
    params = parse_qs(fragment)

    access_token = params.get("access_token", [None])[0]
    expires_in = params.get("expires_in",[None])[0]
    if not access_token:
        raise KeyError("未在回调 URL 中找到 access_token，请检查输入的 URL 是否正确")
    UserManager.add_user(username,{
        "access_token":access_token,
        "expires_at":int(expires_in+time.time())
    })
    context.access_token = access_token
    context.username = username
    context.need_relogin = False

def is_valid_access_token(access_token:str,expires_at:int=None)->bool:
    not_expired = True
    if expires_at:
        not_expired = expires_at > (time.time()+60*10)
    return access_token and access_token.strip() != "" and not_expired

def handle(context: Context, args):
    username = args.username
    user_data = UserManager.get_user(username)
    if context.need_relogin or not user_data:
        login_guide(username,context)
    else:
        access_token = user_data["access_token"]
        expires_at = user_data["expires_at"]
        if is_valid_access_token(access_token,expires_at):
            context.access_token = access_token
            context.username = username
        else:
            login_guide(username,context)
