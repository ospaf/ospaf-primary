import sys
sys.path.append("../../..")

import threading

import base64
import json
import urllib
import urllib2
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase
from GithubUser.DMLib.DMTask import DMTask
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers

def date_string_to_int(date_string):
    num = int(date_string[0:4])*10000+int(date_string[5:7])*100+int(date_string[8:10])
    return num

class GithubUser:
    def __init__(self, task):
        self.task = task
        self.db = DMDatabase().getDB()

    def get_user(self, gh_user_login):
        url = "https://api.github.com/users/"+gh_user_login
        print gh_user_login
        return DMSharedUsers().readURL(url)

    def get_user_list(self, gh_user_id):
        url = "https://api.github.com/users?since="+`gh_user_id`+"&page_size=100";
        print url
        return DMSharedUsers().readURL(url)

    def get_user_from_list(self, user_list):
        last_id = 0
        for item in user_list:
            ret_val = self.get_user(self, item["login"])
            last_id = item["id"]
            if ret_val["error"] == 1:
                self.task.error({"login": item["login"], "id": item["id"], "message": "error in upload_user_event"})
                continue
            else:
                val = ret_val["val"]
                val["update_date"] = datetime.datetime.utcnow()
                created_at_string = val["created_at"]
                updated_at_string = val["updated_at"]
                created_at_int = date_string_to_int(created_at_string)
                updated_at_int = date_string_to_int(updated_at_string)
                val["created_at_int"] = created_at_int
                val["updated_at_int"] = updated_at_int
                if self.db["user"].find_one({"login": item["login"]}):
                    self.db["user"].update({"login": item["login"]}, {"$set": val})
                else:
                    self.db["user"].insert(val)
        return last_id

    def validateTask(self):
        info = self.task.getInfo()
        if info["start"] > info["end"]:
            print "Error in the task"
            return 0
        return 1

    def runTask(self):
        info = self.task.getInfo()
        if info["action_type"] == "loop":
            self.runLoopTask()
        elif info["action_type"] == "update":
            self.runUpdateTask()

    def runUpdateTask(self):
        if self.validateTask() == 0:
            return
        if self.task.updateStatus("running") != 0:
            return

        info = self.task.getInfo()
        start_id = info["start"]
        if info.has_key("current"):
            start_id = info["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        last_id = start_id
        while 1:
            res = self.get_user_list(last_id)
            if res["error"] == 1:
                self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                break
            elif len(res["val"]) == 0:
                self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                break
            else:
                last_id = self.get_user_from_list(res["val"])
                if last_id == 0:
                    self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                    break
                if len(res["val"]) < 100:
#end id == current id
                    self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                    break
                else:
                    self.task.update({"current": last_id, "update_date": datetime.datetime.utcnow()})

        print "Task finish, exiting the thread"

    def runLoopTask(self):
        if self.validateTask() == 0:
            return
        if self.task.updateStatus("running") != 0:
            return

        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]
        if info.has_key("current"):
            start_id = info["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        last_id = start_id
        while last_id <= end_id:
            res = self.get_user_list(last_id)
            if res["error"] == 1:
                self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                break
            elif len(res["val"]) == 0:
                self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                break
            else:
                last_id = self.get_user_from_list(res["val"])
                if len(res["val"]) < 100:
#end id == current id
                    self.task.update({"status": "finish", "current": last_id, "end": last_id, "update_date": datetime.datetime.utcnow()})
                    break
                else:
                    self.task.update({"current": last_id, "update_date": datetime.datetime.utcnow()})

        print "Task finish, exiting the thread"

# very important, the entry function
def init_user_task():
# TODO: 1000 is system defined, maybe add to DMTask? or config file?
    gap = 1000
    start = 0
# end id is now set to 10300000
    end = 10300
    db = DMDatabase().getDB()
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_users", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)

def get_last_saved_id():
    db = DMDatabase().getDB()
    res = db["user"].find().sort("id", pymongo.DESCENDING).limit(1)
    for item in res:
        return item["id"]
    return 0
  
# unlike init_user_task, this is used to get new users
def updated_user_task():
    last_id  = get_last_saved_id()
    task = DMTask()
    val = {"name": "get_users", "action_type": "update", "start": last_id, "end": 0}
    task.init("github", val)


#updated_user_task()

