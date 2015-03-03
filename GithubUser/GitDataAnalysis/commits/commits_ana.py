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

def is_repo_cache(db, repo):
#    return id, I sugguest
    res = db["commit_repo_cache"].find_one({"repos": repo})
    if res:
        return res
    else:
        return None

def merge_repo_cache(db, item, repos):
    repos_list = item["repos"]
    for repo in repos:
        if repo in repos_list:
            continue
        else:
            repos_list.append(repo)
    print "update"
    count = len(repos_list)
    db["commit_repo_cache"].update({"_id": item["_id"]}, {"$set": {"repos": repos_list, "count": count}})

def add_repo_cache(db, repos):
    if len(repos) > 1:
        print "insert"
        db["commit_repo_cache"].insert({"repos": repos, "count": len(repos)})

def get_dup_repos (db):
    res = db["commit_check_result"].find({"count":{"$gt": 1}, "visited":{"$exists": False}})
    if res:
        for item in res:
            merge = False
            for repo in item["repos"]:
                repo_cache_item = is_repo_cache(db, repo)
                if repo_cache_item is None:
                    pass
                else:
                    merge_repo_cache(db, repo_cache_item, item["repos"])
                    merge = True
                    break
            if merge == False:
                add_repo_cache(db, item["repos"])
            

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
