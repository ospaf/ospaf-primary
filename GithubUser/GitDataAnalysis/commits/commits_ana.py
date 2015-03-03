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

def get_top_commit_repos (db):
    res = db["commit_check_result"].find({"count":{"$gte": 200}})
    if res:
        for item in res:
            for repo in item["repos"]:
                print repo
                break
#            print item["repos"][0]

# repos: [a, b, x, t]
#     if db has [a, b, c, d, e], count == 1, merge db with repos
#     if db has [a, b, c, d, e], [a, f, g, h, j], [x, y, z] count >1, merge db[1], db[2], db[3] and repos
def merge_repos_cache(db, repos):
    res = db["commit_repo_cache"].find({"repos": {"$in": repos}})
    count = res.count()
    if count > 0:
        repos_list = repos
        for item in res:
            if count == 1:
                merge_repo(db, item, repos)
                return True
            else:
                repos_list += item["repos"]
        for item in res:
            db["commit_repo_cache"].remove({"_id": item["_id"]})        
        repos_list = list(set(repos_list))
        add_repo(db, repos_list)
    elif count == 0:
        add_repo(db, repos)

def merge_repo(db, item, repos):
    repos_list = item["repos"] + repos
    repos_list = list(set(repos_list))
    print "update"
    count = len(repos_list)
    db["commit_repo_cache"].update({"_id": item["_id"]}, {"$set": {"repos": repos_list, "count": count}})

def add_repo(db, repos):
    if len(repos) > 1:
        print "insert"
        db["commit_repo_cache"].insert({"repos": repos, "count": len(repos)})

def get_dup_repos (db):
    res = db["commit_check_result"].find({"count":{"$gt": 1}, "visited":{"$exists": False}}).sort("count", pymongo.DESCENDING)
    if res:
        for item in res:
            if len(item["repos"]) == 0:
                continue
            merge_repos_cache(db, item["repos"])
            db["commit_check_result"].update({"_id": item["_id"]}, {"$set": {"visited": True}}})

def main(type):
    timeout = 300
    socket.setdefaulttimeout(timeout)

    db = DMDatabase().getDB()
    if db:
        if type == "top":
            get_top_commit_repos(db)
        elif type == "dup":
            get_dup_repos(db)

type = "top"
type = "dup"
main(type)
