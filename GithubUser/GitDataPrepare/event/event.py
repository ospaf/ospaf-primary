import sys
sys.path.append("../../..")
import re
import threading
import socket
import base64
import json
import httplib
import urllib
import urllib2
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers
from GithubUser.DMLib.DMTask import DMTask

class GithubEvent:
    def __init__(self, task):
        self.task = task
        self.db = DMDatabase().getDB()

    def append_event(self, gh_user_id, page):
        url = "https://api.github.com/users/"+gh_user_id+"/events?page="+str(page);
        return DMSharedUsers().readURL(url)

    def upload_user_event(self, user_login):
        need_update = 0
        old_res = self.db["event"].find_one({"login": user_login})
        if old_res:
            return 0

        new_res = self.user_event_list(user_login)
        if (new_res["error"] == 1):
#TODO we should save this error in order to do it again!
            return 1

        count = len(new_res["val"])

        if count > 0:
            print user_login + " added with " + str(count) + " counts"
        self.db["event"].insert({"login": user_login, "event": new_res["val"], "count": count, "update_date": datetime.datetime.utcnow()})
        return 0

    def user_event_list(self, user_login):
        res = []
        i = 1
        while 1:
            ret_val = self.append_event(user_login, i)
            if ret_val["error"] == 1:
                if i > 2:
#   "message": "In order to keep the API fast for everyone, pagination is limited for this resource. Check the rel=last link relation in the Link response header to see how far back you can traverse.",
#  "documentation_url": "https://developer.github.com/v3/#pagination"
                    return {"error": 0, "val": res}
                else:
                    return {"error": 1}
            if len(ret_val["val"]) > 0:
                res += ret_val["val"]
                if len(ret_val["val"]) < 30:
                    break
            else:
                break
            i += 1
# simply return if event > 10..
            if i > 10:
                break

        return {"error": 0, "val": res}

    def validateTask(self):
        info = self.task.getInfo()
        if info["start"] > info["end"]:
            print "Error in the task"
            return 0
        return 1

# in case same client cannot access our db
# we give them the logins and get json plain file in return
    def generate(self, output_file):
        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]
        if info.has_key("current"):
            start_id = info["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["user"].find(query).sort("id", pymongo.ASCENDING)
        res_len = res.count()
        i = 0
        fw = open(output_file, "w")
        for item in res:
            fw.write(item["login"])
            fw.write("\n")

#task is the instance of DMTask
    def runTask(self):
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

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["user"].find(query).sort("id", pymongo.ASCENDING)
        res_len = res.count()
        i = 0
        percent_gap = res_len/100
        for item in res:
            updated_date_int = item["updated_at_int"]
            i += 1
            if updated_date_int < 20141000:
                continue 
            ret = self.upload_user_event(item["login"])
            if ret == 1:
#TODO make a better error message
                self.task.error({"login": item["login"], "message": "error in upload_user_event"})
                continue

            if percent_gap == 0:
                percent = 1.0 * i / res_len
                self.task.update({"current": item["id"], "percent": percent, "update_date": datetime.datetime.utcnow()})
#save every 100 calculate 
            elif i%percent_gap == 0:
                percent = 1.0 * i / res_len
                self.task.update({"current": item["id"], "percent": percent, "update_date": datetime.datetime.utcnow()})

        self.task.update({"status": "finish", "current": end_id, "percent": 1.0, "update_date": datetime.datetime.utcnow()})
        print "Task finish, exiting the thread"

def test():
    task1 = DMTask()
    val = {"name": "fake-event", "action_type": "loop", "start": 6001000, "end": 6005000}

    task1.init_test("github", val)
    e1 = GithubEvent(task1)
    e1.runTask()
    task1.remove()

#test()


