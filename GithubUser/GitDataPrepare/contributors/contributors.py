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
        url = "https://api.github.com/repos/"+full_name+"/contributors";
        return DMSharedUsers().readURL(url, {"page": page})

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
#NOTE: if we retry too many times..  the API is easily to reach the limitation
                if (timeout_time < 3):
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
            print "insert " + full_name + " with " + str(count)
            c_item = self.db["contributors"].find_one({"id": id})
            if c_item:
                self.db["contributors"].update({"_id": c_item["_id"]}, {"$set": {"contributors": ret_val["val"], 
                                            "count": count, "update_date": datetime.datetime.utcnow()}})
            else:
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

    def runFix2Task(self):
        if self.validateTask() == 0:
            return
        self.task.updateStatus("fix2-running")

        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]

        con_query = {"id": {"$gte": start_id, "$lt": end_id}, "fork": False, "count": {"$gt": 0}}
        con_res = self.db["contributors"].find(con_query).sort("id", pymongo.ASCENDING)
        for item in con_res:
            p = item["full_name"].find("/")
            item_name = item["full_name"][p+1:-1]
            for contributor in item["contributors"]:
# contributor -- { "contributions" : 6, "login" : "Krzem0", "site_admin" : false, "type" : "User", "id" : 636186 }
                user_res = self.db["user_contributor_result2"].find_one({"id": contributor["id"]})
                if user_res:
                    print "Update " + user_res["login"]
                    contributor_commits = user_res["contributor_commits"]
                    contributor_repos = user_res["contributor_repos"]
                    repo_list = user_res["repo_list"]
                    repo_changed = 0
                    for repo_list_item in repo_list:
                        p = repo_list_item["full_name"].find("/")
                        repo_list_name = repo_list_item["full_name"][p+1:-1]
                        # the repo is much like 'fork', but just without fork mark.. we choose the max commits one
                        if item_name == repo_list_name:
                            if repo_list_item["commits"] < contributor["contributions"]:
                                # contributor_repos is not changed
                                # contributor_repos += 0
                                contributor_commits = user_res["contributor_commits"] - repo_list_item["commits"] + contributor["contributions"]
                                repo_list_item["full_name"] = item["full_name"]
                                repo_list_item["commits"] = contributor["contributions"]
                                repo_changed = 1
                                break
                            else:
                                repo_changed = 2
                                break
                    # no need to update
                    if repo_changed == 2:
                        continue
                    # no exist repo found
                    elif repo_changed == 0:
                        contributor_repos += 1
                        contributor_commits += contributor["contributions"]
                        repo_list.append({"full_name": item["full_name"], "commits": contributor["contributions"]})

                    self.db["user_contributor_result2"].update({"_id": user_res["_id"]}, {"$set": {"contributor_repos": contributor_repos, "contributor_commits": contributor_commits, "repo_list": repo_list}})
                else:
                    repo_list = [{"full_name": item["full_name"], "commits": contributor["contributions"]}]
                    self.db["user_contributor_result2"].insert({"id": contributor["id"], "login": contributor["login"], "contributor_repos": 1, "contributor_commits": contributor["contributions"], "repo_list": repo_list})

        self.task.update({"status": "fixed2"})
        print "Fix2 task finish, exiting the thread"

    def runFixTask(self):
        if self.validateTask() == 0:
            return
        self.task.updateStatus("fix-running")

        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]

        con_query = {"id": {"$gte": start_id, "$lt": end_id}, "fork": {"$exists": False}}
        con_res = self.db["contributors"].find(con_query).sort("id", pymongo.ASCENDING)
        con_list = []
        for item in con_res:
            con_list.append({"id": item["id"], "contributors": item["contributors"], "full_name": item["full_name"]})
        con_len = len(con_list)
        if con_len == 0:
            self.task.update({"status": "fixed"})
            print "Fix task finish, exiting the thread"
            return

        repo_query = {"id": {"$gte": start_id, "$lt": end_id}}
        repo_res = self.db["repositories"].find(repo_query).sort("id", pymongo.ASCENDING)
        repo_list = []
        for item in repo_res:
            repo_list.append({"id": item["id"], "fork": item["fork"]})
        repo_len = len(repo_list)
        repo_end = 0
        i = 0
        print str(con_len) + "  contributors  " + str(len(repo_list)) + " repos  - start " +  str(start_id) + "  end " + str(end_id)
        while i < con_len:
            while repo_end < repo_len and i <= repo_end:
#               print "con " + str(con_list[i]["id"]) + "  repo  " + str(repo_list[repo_end]["id"])
                if con_list[i]["id"] == repo_list[repo_end]["id"]:
                    self.db["contributors"].update({"id": con_list[i]["id"]}, {"$set": {"fork": repo_list[repo_end]["fork"]}})
                    if repo_list[repo_end]["fork"]:
                        repo_end += 1
                        break
                    for user_item in con_list[i]["contributors"]:
                        contributor_repos = 1
                        contributor_commits = user_item["contributions"]
                        user_res = self.db["user_contributor_result"].find_one({"id": user_item["id"]})
                        if user_res:
                            print "Update " + user_res["login"]
                            if user_res.has_key("contributor_commits"):
                                contributor_commits += user_res["contributor_commits"]
                            if user_res.has_key("contributor_repos"):
                                contributor_repos += user_res["contributor_repos"]
                            self.db["user_contributor_result"].update({"_id": user_res["_id"]}, {"$set": {"contributor_repos": contributor_repos, "contributor_commits": contributor_commits}})
                        else:
                            self.db["user_contributor_result"].insert({"id": user_item["id"], "login": user_item["login"], "contributor_repos": contributor_repos, "contributor_commits": contributor_commits})
#                    print str(con_list[i]["id"]) + " Updated"
                    repo_end += 1
                    break
                else:
                    repo_end += 1
            i += 1
        self.task.update({"status": "fixed"})
        print "Fix task finish, exiting the thread"

    def runLoopTask(self):
        if self.validateTask() == 0:
            return
        if self.task.updateStatus("running") != 0:
            return

        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]
#Dliang marks this to do fix work...
        if info.has_key("current"):
#FIXME
#            start_id = info["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["repositories"].find(query).sort("id", pymongo.ASCENDING)
        res_list = []
        for item in res:
            if item.has_key("contributors_count"):
#                print item["full_name"] + " already exist"
                continue
            else:
                res_list.append({"full_name": item["full_name"], "id": item["id"]})

        res_len = len(res_list)
#FIXME
        print "Only " + str(res_len) + "  task remains"
        i = 0
        percent_gap = res_len/100

        for item in res_list:
            i += 1
#            saved_res = self.db["contributors"].find_one({"id": item["id"]})
#            if saved_res:
#                print "How could it possible!\n\n"
#                continue
            self.get_repo_contributors(item["full_name"], item["id"])
#Dliang fix memo
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
    start = 29000
    end = 30900
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

def resolve_contributors_30():
    db = DMDatabase().getDB()

    task1 = DMTask()
    val = {"name": "fake-contributors", "action_type": "loop", "start": 0, "end": 1000}
    task1.init_test("github", val)
    e1 = GithubContributors(task1)

    for num in range(1, 300):
        res = db["contributors"].find({"count": num*30})
        res_list = []
        for item in res:
            res_list.append({"full_name": item["full_name"], "id": item["id"]})
        for item in res_list:
            e1.get_repo_contributors(item["full_name"], item["id"])

#resolve_contributors_30()
#init_contributors_task()
