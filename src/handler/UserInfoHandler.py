from context import Context
from error import InvalidStateError
from api.BDNetdisk import get_user_info

def handle(context: Context, args):
    if not context.is_logged_in:
        raise InvalidStateError("请先登录。您可以运行 `login` 命令进行登录。")
    print(get_user_info(context))