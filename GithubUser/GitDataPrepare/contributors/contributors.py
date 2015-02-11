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

    def get_contributors(self, full_name):
        res = []
        i = 1
        timeout_time = 0
        while 1:
            ret_val = self.append_contributors(full_name, i)
            if ret_val["error"] == 1:
                timeout_time += 1
                if (timeout_time < 10):
                    print "timeout retry " + full_name + " " + str(i) + " " + str(timeout_time) + "times"
                    continue
                else:
                    return {"error": 1}
            timeout_time = 0
            slim_val = self.get_slim(ret_val["val"])
            res += slim_val
            if len(slim_val) < 30:
                    break
            i += 1

        return {"error": 0, "val": res}

    def get_repo_contributors(self, full_name, id):
        ret_val = self.get_contributors(full_name)
        if ret_val["error"] == 1:
#FIXME: dliang: since we have lots of error in current enviornment, or maybe github is slow in react to this call?, don't save it...
            return
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

#return the solved errors
    def error_check (self):
        info = self.task.getInfo()
        print info
        if info["status"] == "init":
            return 0

        count = 0
        if info.has_key("error"):
#FIXME: this is just lazy way, error_count < 10 means the repo is gone, the error is not caused by our program or network..
            if info["error_count"] < 10:
                return 0
            update_error = []
            list = info["error"]
            for item in list:
                full_name = item["full_name"]
                id = item["id"]
                if self.db["contributors"].find_one({"id": id}):
                    count += 1
                    continue
                print "solve error for " + full_name
                ret = self.get_contributors(full_name)
# error
                if ret == 1:
                    update_error.append({"full_name": full_name, "id": id, "message": "error even in double upload_user_event"})
                else:
                    count += 1
            error_len = len(update_error)
            self.task.update({"error": update_error, "error_count": error_len})
        return count

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
            i += 1
            if item.has_key("contributors_count"):
                print item["full_name"] + " already exist"
                continue
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

def resolve_contributors_loop_errors():
    print "resolve contributors errors"
    gap = 1000
    start = 0
    end = 29000
    count = 0
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_contributors", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r = GithubContributors(task)
        res = r.error_check()
        count += res
    print str(count) + " errors solved"


# unlike init_contributors_task, this is used to get new contributorss
def updated_contributors_task():
    last_id  = get_last_saved_id()
    task = DMTask()
    val = {"name": "get_contributors", "action_type": "update", "start": last_id, "end": 0}
    task.init("github", val)

#init_contributors_task()
#resolve_contributors_loop_errors()
