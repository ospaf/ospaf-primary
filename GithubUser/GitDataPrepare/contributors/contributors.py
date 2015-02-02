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

class GithubContributors:
    def __init__(self, task):
        self.task = task
        self.db = DMDatabase().getDB()

#https://developer.github.com/v3/repos
#GET /repos/:owner/:repo
#List contributors : /repos/:owner/:repo/contributors
    def append_contributors(self, full_name, page):
        url = "https://api.github.com/repos/"+full_name+"/contributors?page="+str(page);
        return DMSharedUsers().readURL(url)

    def get_slim(self, ret_val):
        slim_val = []
        for item in ret_val:
            slim_val.append({"login": item["login"], "id": item["id"], "type": item["type"],
                             "site_admin": item["site_admin"], "contributions": item["contributions"]})
        return slim_val

    def get_contributors(self, user_login):
        res = []
        i = 1
        while 1:
            ret_val = self.append_contributors(user_login, i)
            if ret_val["error"] == 1:
                if i > 2:
#   "message": "In order to keep the API fast for everyone, pagination is limited for this resource. Check the rel=last link relation in the Link response header to see how far back you can traverse.",
#  "documentation_url": "https://developer.github.com/v3/#pagination"
                    return {"error": 0, "val": res}
                else:
                    return {"error": 1}
            slim_val = self.get_slim(ret_val["val"])
            res += slim_val
            if len(slim_val) < 30:
                    break
            i += 1

        return {"error": 0, "val": res}

    def get_repo_contributors(self, full_name, id):
        ret_val = self.get_contributors(full_name)
        if ret_val["error"] == 1:
            self.task.error({"full_name": full_name, "id": id, "message": "error in upload_contributors_contributors"})
        else:
            count = len(ret_val["val"])
            print "insert " + full_name + "with " + str(count)
            self.db["contributors"].insert({"full_name": full_name, "id": id, "contributors": ret_val["val"], 
                                            "count": count, "update_date": datetime.datetime.utcnow()})
            self.db["repositories"].update({"full_name": full_name, "id": id}, {"$set": {"contributors_count": count}})

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
        print "Not implemented"
        return
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

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["repositories"].find(query).sort("id", pymongo.ASCENDING)
        res_list = []
        for item in res:
            res_list.append({"full_name": item["full_name"], "id": item["id"]})
        res_len = len(res_list)
        i = 0
        percent_gap = res_len/100

        for item in res_list:
            self.get_repo_contributors(item["full_name"], item["id"])

            if percent_gap == 0:
                percent = 1.0 * i / res_len
                self.task.update({"current": item["id"], "percent": percent, "update_date": datetime.datetime.utcnow()})
#save every 100 calculate 
            elif i%percent_gap == 0:
                percent = 1.0 * i / res_len
                self.task.update({"current": item["id"], "percent": percent, "update_date": datetime.datetime.utcnow()})

        self.task.update({"status": "finish", "current": end_id, "percent": 1.0, "update_date": datetime.datetime.utcnow()})
        print "Task finish, exiting the thread"

# very important, the entry function
def init_contributors_task():
# 1000 is system defined, maybe add to DMTask? or config file?
    gap = 1000
    start = 0
# end id is now set to 29000000
    end = 29000
    db = DMDatabase().getDB()
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_contributors", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)

# unlike init_contributors_task, this is used to get new contributorss
def updated_contributors_task():
    last_id  = get_last_saved_id()
    task = DMTask()
    val = {"name": "get_contributors", "action_type": "update", "start": last_id, "end": 0}
    task.init("github", val)

#init_contributors_task()
