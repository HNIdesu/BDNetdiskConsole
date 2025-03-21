import os.path as Path
import json as JSON

config_path = Path.abspath("config.json")
if not Path.exists(config_path):
    with open(config_path,"w",encoding="utf-8") as sw:
        sw.write("{}")

def get_app_key()->str:
    with open(config_path,"r",encoding="utf-8") as sr:
        json = JSON.loads(sr.read())
        if "app_key" in json:
            return json["app_key"]
        else:
            return None