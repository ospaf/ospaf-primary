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

def add_commit (db, sha, full_name):
    res = db["commit_check_result"].find_one({"sha":sha})
    if res:
        repo_list = res["repos"]
        if full_name in repo_list:
            print "commit with sha already exist"
            return
        else:
            repo_list.append(full_name)
            db["commit_check_result"].update({"_id": res["_id"]}, {"$set": {"repos": repo_list, "count": res["count"]+1}})
    else:
        db["commit_check_result"].insert({"sha": sha, "repos": [full_name], "count":1})

def get_certain_commits(full_name, param):
    url = "https://api.github.com/repos/"+full_name+"/commits"
    print url
    return DMSharedUsers().readURL(url, param)

def get_commits(db, full_name, date_list):
    for item in date_list:
        ret_val = get_certain_commits(full_name, item)
        if ret_val["error"] == 0:
            if len(ret_val["val"]) > 0:
                print "Get " + full_name
                for commit in ret_val["val"]:
                    add_commit (db, commit["sha"], full_name)

def get_date_list():
    date_list = []
    for year in range(2004, 2015):
        time_slot = {"since": str(year)+"-10-16T01:01:01Z", "until": str(year)+"-11-16T01:01:01Z"}
        date_list.append(time_slot)
    return date_list

def get_commit_repos_by_query(db, query):
    res =db["user_contributor_result2"].find(query)
    date_list = get_date_list()
    i = 0
    for item in res:
        i += 1
        print i

        if db["commit_check_meta_result"].find_one({"login": item["login"]}):
            print item["login"] + " already exist"
            continue
        repo_list = item["repo_list"]
        for repo in repo_list:
           #if the repo is already added, no need to re-generate that 
           if db["commit_check_meta_result"].find_one({"full_name": repo["full_name"]}):
               continue
           get_commits(db, repo["full_name"], date_list)
           db["commit_check_meta_result"].insert({"full_name": repo["full_name"]})
        db["commit_check_meta_result"].insert({"login": item["login"]})

#TODO
def get_commit_repos_by_user_repos(db, user):
    res = db.user_repos.find_one({"login": user})
    for item in res["repos"]:
        if item["full_name"] == "openstack/openstack":
            continue
        print item["full_name"]

def get_commit_repos_by_user(db, user):
    res =db["user_contributor_result2"].find_one({"login": user})
    if res:
        date_list = get_date_list()
        repo_list = res["repo_list"]
        i = 0
        for repo in repo_list:
           i+=1
           print i
           #if the repo is already added, no need to re-generate that 
           if db["commit_check_meta_result"].find_one({"full_name": repo["full_name"]}):
               print repo["full_name"] + "  already exist"
               continue
           get_commits(db, repo["full_name"], date_list)
           db["commit_check_meta_result"].insert({"full_name": repo["full_name"]})

def get_commit_repos_by_users(db, user_list):
    for user in user_list:
        print user

        if db["commit_check_meta_result"].find_one({"login": user}):
            print user + " already exist"
            continue

        get_commit_repos_by_user(db, user)
        db["commit_check_meta_result"].insert({"login": user})

def init_users_thread_by_query(db, query):
    pieces = 100
    db = DMDatabase().getDB()
    i = 0
    res =db["user_contributor_result2"].find(query)
    user_list = []
    for item in res:
        i += 1
        user_list.append(item["login"])
        if i%pieces == 0:
            task = DMTask()
            val = {"name": "get_commit_check", "action_type": "loop", "query": str(query), "users": user_list, "start": 800000 + i-100, "end": 800000 + i}
            task.init("github", val)
            user_list = []

    if i%pieces != 0:
        task = DMTask()
        val = {"name": "get_commit_check", "action_type": "loop", "query": str(query), "users": user_list, "start": 800000 + i-i%pieces, "end": 800000 + 1}
        task.init("github", val)
    return

user_thread = []

class myThread (threading.Thread):
    def __init__(self, db, val):
        threading.Thread.__init__(self)
        self.db = db
        self.val = val
        self.task = DMTask()
        self.task.init("github", val)

    def run(self):
        print "Start the thread" + str(self.val)
        self.task.update({"status": "running", "percent": 0.0, "update_date": datetime.datetime.utcnow()})
        get_commit_repos_by_users(self.db, self.val["users"])
        self.task.update({"status": "finish", "percent": 1.0, "update_date": datetime.datetime.utcnow()})

        print "Exist the thread"

class myThread1 (threading.Thread):
    def __init__(self, db, val):
        threading.Thread.__init__(self)
        self.db = db
        self.val = val

    def run(self):
        print "Start the thread" + self.val
        get_commit_repos_by_user(self.db, self.val)
        print "Exist the thread"

class myThread2 (threading.Thread):
    def __init__(self, db, val):
        threading.Thread.__init__(self)
        self.db = db
        self.val = val

    def run(self):
        print "Start the thread" + self.val
        date_list = get_date_list()
        get_commits(self.db, self.val, date_list)
        print "Exist the thread"

def run_task():
    for item in user_thread:
        item.start()

def run_free_task(db, num):
    query = {"col": "github", "num": num, "query": {"status": "running", "name": "get_commit_check"}}
    res = DMTask().getFreeTasks(query)
    i = 0
    for item in res:
        new_thread = myThread(db, item)
        user_thread.append(new_thread)
        i += 1
    print str(i) + " task received, start to run them!\n\n\n\n"
    run_task()

def get_unfinished_users(db):
    client = DMDatabase().getClient()
    res = client["task"]["github"].find({"status":"running", "name": "get_commit_check"})
    users = []
    for item in res:
        for item_user in item["users"]:
            if db["commit_check_meta_result"].find_one({"login": item_user}):
                print "exist"
            else:
                users.append(item_user)

    for user in users:
        new_thread = myThread1(db, user)
        user_thread.append(new_thread)
    print str(len(users)) + " task received, start to run them!"
    run_task()

def get_unfinished_repos(db):
    client = DMDatabase().getClient()
    res = client["task"]["github"].find({"status":"running", "name": "get_commit_check"})
    repos = []
    for item in res:
        for item_user in item["users"]:
            if db["commit_check_meta_result"].find_one({"login": item_user}):
                continue
            else:
                user_res =db["user_contributor_result2"].find_one({"login": item_user})
                if user_res:
                    repo_list = user_res["repo_list"]
                    repos += repo_list
    unfinish_repos = []
    for item in repos:
        unfinish_repos.append(item["full_name"])
    unfinish_repos = list(set(unfinish_repos))
    repos = []
    for item in unfinish_repos:
        if item.startswith("GITenberg/"):
            continue
        if db["commit_check_meta_result"].find_one({"full_name": item}):
            continue
        else:
            repos.append(item)

    for repo in repos:
        new_thread = myThread2(db, repo)
        user_thread.append(new_thread)
    print str(len(repos)) + " task received, start to run them!"
    run_task()

def main(type):
    timeout = 300
    socket.setdefaulttimeout(timeout)

    print "Account has " + str(DMSharedUsers().getRemaining()) + " API calls"

    db = DMDatabase().getDB()
    if db:
        if type == "user":
            user = "torvalds"
            get_commit_repos_by_user(db, user)
        if type == "user_repos":
            user = "openstack"
            get_commit_repos_by_user_repos(db, user)
        elif type == "query":
            query = {"contributor_repos": {"$gte": 200}}
            get_commit_repos_by_query(db, query)
        elif type == "init_task":
            query = {"contributor_repos": {"$gte": 100, "$lt": 200}}
            init_users_thread_by_query(db, query)
        elif type == "run_task":
            run_free_task(db, 60)
        elif type == "un_user":
            get_unfinished_users(db)
        elif type == "un_repo":
            get_unfinished_repos(db)


type = "user_repos"
type = "user"
type = "query"
type = "init_task"
type = "run_task"
type = "un_user"
type = "un_repo"
main(type)
