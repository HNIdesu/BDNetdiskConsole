import os.path as Path
import json as JSON
config_path = Path.abspath("users.json")
if not Path.exists(config_path):
    with open(config_path,"w",encoding="utf-8") as sw:
        sw.write("{}")

def get_user(username:str)->any:
    with open(config_path,"r",encoding="utf-8") as sr:
        json = JSON.loads(sr.read())
        if username in json:
            return json[username]
        else:
            return None

def all_users()->any:
     with open(config_path,"r",encoding="utf-8") as sr:
        return JSON.loads(sr.read())

def add_user(username:str,data:any):
    with open(config_path,"r",encoding="utf-8") as sr:
        json = JSON.loads(sr.read())
        json[username] = data
    with open(config_path,"w",encoding="utf-8") as sw:
        sw.write(JSON.dumps(json))

def delete_user(username:str):
    with open(config_path,"r",encoding="utf-8") as sr:
        json = JSON.loads(sr.read())
        if username in json:
            json.pop(username)
    with open(config_path,"w",encoding="utf-8") as sw:
        sw.write(JSON.dumps(json))

