import sys

import base64
import json
import urllib
import urllib2
import datetime
import pymongo
from pymongo import MongoClient

# like the seeds
# TODO should add some famous id 
init_user = ["initlove"]

user_pass = [
    {"user":"githublover007", "password": "qwe123456", "count": 0},
    {"user":"githublover008", "password": "qwe123456", "count": 0},
    {"user":"githublover005", "password": "qwe123456", "count": 0},
    {"user":"githublover006", "password": "qwe123456", "count": 0}
]

def init_db ():
    _db_addr = "147.2.207.55"
    _db_port = 27017
    _db_name = "github"

    client = MongoClient(_db_addr, _db_port)
    db = client[_db_name]
    return db

def get_free_user():
    min_count = 0
    i = 0
    for item in user_pass:
        if (item["count"] < user_pass[min_count]["count"]):
            min_count = i
        i += 1
    user_pass[min_count]["count"] += 1
    return min_count

# In github - follower, the default page_size is 30 and we cannot change it. 
#    seems...Correct me if I were wrong
def append_followers(gh_user_id, page):
    url = "https://api.github.com/users/"+gh_user_id+"/followers?page="+str(page);
    req = urllib2.Request(url)
    i = get_free_user()
    username = user_pass[i]["user"]
    password = user_pass[i]["password"]
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)   

    res_data = urllib2.urlopen(req)
    res = res_data.read()

    val = json.loads(res)
    ret_val = []
    for item in val:
        ret_val.append ({"id": item["id"], "login": item["login"]})
    return ret_val

def user_followers_count(db, user_login):
    dc = db["user"]
    result = dc.find_one({"login": user_login})
    if (result):
        return result["followers"]
    else:
        return -1

def main():
    db = init_db()
#    user_login = "marguerite"
    user_login = "initlove"
    upload_user_followers(db, user_login)
    
def upload_user_followers(db, user_login):
    need_update = 0
    res = db["followers"].find_one({"login": user_login})
    if res:
        count = user_followers_count(db, user_login)
        res_len = len(res["followers"])
        if (count == res_len): 
            print "saved"
            return
        else:
# Check if we need to upload
# TODO  better one
            need_update = 1

    res = user_followers_list(db, user_login)
    if need_update == 0:
        val = {"login": user_login, 
               "followers": res,
               "update_date": datetime.datetime.utcnow()
              }
        db["followers"].insert(val)
        print "insert " + user_login
    else:
        val = {"$set": {"update_date": datetime.datetime.utcnow(),
                        "followers": res}}
        db["followers"].update({"login":user_login}, val})
        print "update " + user_login

    for item in res:
        upload_user_followers(db, item["login"])
        

def user_followers_list(db, user_login):
    res = []
    count = user_followers_count(db, user_login)
    if count <= 0:
        return res
# 30 is github system defined
    page_size = 30
    pages = count/30 + 1
    i = 1
    while i <= pages:
        ret_val = append_followers(user_login, i)
        res += ret_val
        i += 1

    return res

main()
