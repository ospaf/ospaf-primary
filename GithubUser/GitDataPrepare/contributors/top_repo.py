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

def top_append_contributors(full_name, page):
    url = "https://api.github.com/repos/"+full_name+"/contributors?page="+str(page);
    print url
    return DMSharedUsers().readURL(url)

def top_get_slim(ret_val):
    slim_val = []
    for item in ret_val:
        slim_val.append({"login": item["login"], "id": item["id"], "type": item["type"],
                             "site_admin": item["site_admin"], "contributions": item["contributions"]})
    return slim_val

def top_get_contributors(full_name, id):
    res = []
    i = 1
    while 1:
        ret_val = top_append_contributors(full_name, i)
        if ret_val["error"] == 1:
#I'm afraid I should not use i > 2...
            db["contributors_error"].insert({"full_name": full_name, "id": id})
            return {"error": 1}
        slim_val = top_get_slim(ret_val["val"])
        res += slim_val
        if len(slim_val) < 30:
            break
        i += 1
    return {"error": 0, "val": res}

def top_fork():
    db = DMDatabase().getDB()
    num = 10000
    res = db["repositories"].find().sort("forks_count", pymongo.DESCENDING).limit(num)
    for item in res:
        if item.has_key("contributors_count"):
            continue
        full_name = item["full_name"]
        id = item["id"]
        ret_val = top_get_contributors(full_name, id)
        if ret_val["error"] == 1:
            pass
        else:
            count = len(ret_val["val"])
            db["contributors"].insert({"full_name": full_name, "id": id, "contributors": ret_val["val"], 
                                            "count": count, "update_date": datetime.datetime.utcnow()})
            db["repositories"].update({"full_name": full_name, "id": id}, {"$set": {"contributors_count": count}})
            print "insert " + full_name + "with " + str(count)

top_fork()
