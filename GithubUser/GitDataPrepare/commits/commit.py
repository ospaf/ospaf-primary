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

class GithubCommit:
    def __init__(self, task):
        self.task = task
        self.db = DMDatabase().getDB()
        info = self.task.getInfo()
        self.repo = info["start"]

    def get_commit(self, page):
        url = "https://api.github.com/repos/"+ self.repo + "/commits"
        return DMSharedUsers().readURL(url, {"page": page})

    def validateTask(self):
        return 1

    def runTask(self):
        info = self.task.getInfo()
        if info["action_type"] == "loop":
            self.runLoopTask()

    def runLoopTask(self):
        if self.validateTask() == 0:
            return
        if self.task.updateStatus("running") != 0:
            return

        info = self.task.getInfo()
        page = 1
        if info.has_key("current"):
            page = info["current"] + 1
            #TODO. since commit will be increasing, we need to get 'new ones'
            print "Find unfinished task, continue to work at " + str(page)

        while True:
            res = self.get_commit(page)
            if res["error"] == 1:
                self.task.update({"status": "error", "current": page-1, "update_date": datetime.datetime.utcnow()})
            elif len(res["val"]) == 0:
                self.task.update({"status": "finish", "current": page, "update_date": datetime.datetime.utcnow()})
            else:
                if len(res["val"]) < 30:
                    self.task.update({"status": "finish", "current": page, "update_date": datetime.datetime.utcnow()})
                else:
                    self.task.update({"current": page, "update_date": datetime.datetime.utcnow()})
                for item in res["val"]:
                    item["full_name"] = self.repo
                    item["uniq"] = self.repo + item["sha"]
                    if self.db["commit"].find_one({"uniq": item["uniq"]}):
                        print "commit exist"
                        continue
                    else:
                        print self.repo + " " + str(page) + " insert"
                        self.db["commit"].insert(item)
            page += 1

        print "Task finish, exiting the thread"

# very important, the entry function
def init_commit_task(db, repo):
    task = DMTask()
    item = db["repositories"].find_one({"full_name": repo})
    if item:
        id = item["id"]
        val = {"name": "get_commit", "action_type": "loop", "start": repo, "end": id}
        task.init("github", val)

#init_commit_task()

def init_commit_task_by_user():
    db = DMDatabase().getDB()
    user = "torvalds"
    res =db["user_contributor_result2"].find_one({"login": user})
    if res:
        repo_list = res["repo_list"]
        for repo in repo_list:
            init_commit_task(db, repo["full_name"])

#init_commit_task_by_user()
