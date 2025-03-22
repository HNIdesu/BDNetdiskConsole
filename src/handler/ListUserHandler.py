from context import Context
from manager import UserManager

def handle(context: Context, args):
    users:dict = UserManager.all_users()
    for name in users.keys():
        print(name)