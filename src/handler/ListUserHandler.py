from context import Context
from handler import BaseHandler
from manager import UserManager

class ListUserHandler(BaseHandler):
    def handle(self, context: Context, args):
        users:dict = UserManager.all_users()
        for name in users.keys():
            print(name)