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
    if date_string:
        num = int(date_string[0:4])*10000+int(date_string[5:7])*100+int(date_string[8:10])
        return num
    else:
        return 0

class GithubRepositories:
    def __init__(self, task):
        self.task = task
        self.db = DMDatabase().getDB()

#https://developer.github.com/v3/repos
#GET /repos/:owner/:repo
#List contributors : /repos/:owner/:repo/contributors
    def get_repository(self, gh_repositories_item):
# "full_name": "wycats/merb-core"
        repo_name = gh_repositories_item["full_name"]
        url = "https://api.github.com/repos/"+ repo_name
        return DMSharedUsers().readURL(url, {})

    def get_repositories_list(self, gh_repositories_id):
        url = "https://api.github.com/repositories";
        return DMSharedUsers().readURL(url, {"since": gh_repositories_id, "page_size": 100})

    def insert_data(self, val):
        key_prop = ["id", "name", "full_name", "private", "description", "fork", "created_at", "updated_at", "pushed_at",
                    "size", "stargazers_count", "watchers_count", "language", "has_issues", "has_downloads", "has_wiki",
                    "has_pages", "forks_count", "mirror_url", "open_issues_count", "forks", "open_issues", "watchers",
                    "default_branch", "network_count", "subscribers_count"]
        own_prop = ["login", "id", "type", "site_admin"]

        new_val = {"owner": {}}
        for item in key_prop:
            new_val[item] = val[item]
        for item in own_prop:
            new_val["owner"][item] = val["owner"][item]
        print "insert " + val["full_name"]
        created_at_string = val["created_at"]
        updated_at_string = val["updated_at"]
        pushed_at_string = val["pushed_at"]
        created_at_int = date_string_to_int(created_at_string)
        updated_at_int = date_string_to_int(updated_at_string)
#the pushed_at prop will be None...
        pushed_at_int = date_string_to_int(pushed_at_string)
        new_val["created_at_int"] = created_at_int
        new_val["updated_at_int"] = updated_at_int
        new_val["pushed_at_int"] = pushed_at_int
        new_val["update_date"] = datetime.datetime.utcnow()

        self.db["repositories"].insert(new_val)

    def get_repositories_from_list(self, repositories_list):
        last_id = 0
        for item in repositories_list:
            last_id = item["id"]
            if self.db["repositories"].find_one({"id": item["id"]}):
                continue
            ret_val = self.get_repository(item)
            if ret_val["error"] == 1:
                self.task.error({"full_name": item["full_name"], "id": item["id"], "message": "error in upload_repositories_event"})
                continue
            else:
                self.insert_data(ret_val["val"])
        return last_id

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
        if info["status"] != "finish":
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
                if self.db["repositories"].find_one({"id": id}):
                    count += 1
                    continue
                print "solve error for " + full_name
                ret = self.get_repository(item)
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
            res = self.get_repositories_list(last_id)
            if res["error"] == 1:
                self.task.error({"since": last_id, "message": "error in upload_repositories_event"})
                self.task.update({"status": "finish", "current": last_id, "update_date": datetime.datetime.utcnow()})
                return
            elif len(res["val"]) == 0:
                self.task.update({"status": "finish", "current": last_id, "update_date": datetime.datetime.utcnow()})
                break
            else:
                last_id = self.get_repositories_from_list(res["val"])
                if last_id == 0:
                    break
                if len(res["val"]) < 100:
#end id == current id
                    break
                else:
                    self.task.update({"current": last_id, "update_date": datetime.datetime.utcnow()})

        self.task.update({"status": "finish", "current": last_id, "update_date": datetime.datetime.utcnow()})
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
        print "last id " + str(last_id) + "  end id" + str(end_id)
        while last_id <= end_id:
            res = self.get_repositories_list(last_id)
            if res["error"] == 1:
#FIXME: if error, we should continue..
                self.task.error({"since": last_id, "message": "error in upload_repositories_event"})
                self.task.update({"status": "finish", "current": last_id, "update_date": datetime.datetime.utcnow()})
                break
            elif len(res["val"]) == 0:
                self.task.update({"status": "finish", "current": last_id, "update_date": datetime.datetime.utcnow()})
                break
            else:
                last_id = self.get_repositories_from_list(res["val"])
                if len(res["val"]) < 100:
#end id == current id
                    self.task.update({"status": "finish", "current": last_id, "update_date": datetime.datetime.utcnow()})
                    break
                else:
                    self.task.update({"current": last_id, "update_date": datetime.datetime.utcnow()})

        print "Task finish, exiting the thread"

# very important, the entry function
def init_repositories_task():
# TODO: 1000 is system defined, maybe add to DMTask? or config file?
    gap = 1000
    start = 10300
# end id is now set to 29000000
    end = 29000
    db = DMDatabase().getDB()
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_repositories", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)

def get_last_saved_id():
    db = DMDatabase().getDB()
    res = db["repositories"].find().sort("id", pymongo.DESCENDING).limit(1)
    for item in res:
        return item["id"]
    return 0
  
# unlike init_repositories_task, this is used to get new repositoriess
def updated_repositories_task():
    last_id  = get_last_saved_id()
    task = DMTask()
    val = {"name": "get_repositories", "action_type": "update", "start": last_id, "end": 0}
    task.init("github", val)

def resolve_event_loop_errors():
    print "resolve event errors"
    gap = 1000
    start = 0
# end id is now set to 10300000
    end = 29000
    count = 0
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_repositories", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r = GithubRepositories(task)
        res = r.error_check()
        count += res
    print str(count) + " errors solved"

#most error comes from: Forbidden
#https://help.github.com/articles/dmca-takedown-policy/
#https://github.com/Bob-Grind/Website_Rule
def resolve_event_errors():
    client = DMDatabase().getClient()
    res = client["task"]["github"].find({"name": "get_repositories", "error_count": {"$gte": 10}})
    count = 0
    for item in res:
        task = DMTask()
        val = {"name": "get_repositories", "action_type": "loop", "start": item["start"], "end": item["end"]}
        task.init("github", val)
        r = GithubRepositories(task)
        res = r.error_check()
        count += res
    print str(count) + " errors solved"

#updated_repositories_task()

#init_repositories_task()
#resolve_event_errors()
