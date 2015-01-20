import sys
import threading

import base64
import json
import urllib
import urllib2
import datetime
import pymongo
from pymongo import MongoClient

user_thread = []

# like the seeds
# I got them by search followers > 500
init_user = [
"bbatsov",
"PaulKinlan",
"lepture",
"ivaynberg",
"mitchellh",
"schmittjoh",
"akrabat",
"yihui",
"mojombo",
"MartianZ",
"SamyPesse",
"chad",
"maxogden",
"sindresorhus",
"passy",
"numbbbbb",
"philsturgeon",
"bkeepers",
"mubix",
"raganwald",
"evanw",
"dhg",
"nvie",
"cheeaun",
"magnars",
"svenfuchs",
"codegangsta",
"igorw",
"gregkh",
"loiane",
"jashkenas",
"BrendanEich",
"jakearchibald",
"astaxie",
"lexrus",
"omz",
"phuslu",
"hueniverse",
"progrium",
"HenrikJoreteg",
"al3x",
"purcell",
"fnando",
"evanphx",
"caitp",
"kytrinyx",
"toddmotto",
"JakeWharton",
"aaronsw",
"defunkt",
"tapajos"
]

user_pass = [
    {"user":"githublover001", "password": "qwe123456", "count": 0},
    {"user":"githublover002", "password": "qwe123456", "count": 0},
    {"user":"githublover003", "password": "qwe123456", "count": 0},
    {"user":"githublover004", "password": "qwe123456", "count": 0},
    {"user":"githublover005", "password": "qwe123456", "count": 0},
    {"user":"githublover006", "password": "qwe123456", "count": 0},
    {"user":"githublover007", "password": "qwe123456", "count": 0},
    {"user":"githublover008", "password": "qwe123456", "count": 0},
    {"user":"githublover009", "password": "qwe123456", "count": 0},
    {"user":"githublover010", "password": "qwe123456", "count": 0},
    {"user":"githublover011", "password": "qwe123456", "count": 0},
    {"user":"githublover012", "password": "qwe123456", "count": 0},
    {"user":"githublover013", "password": "qwe123456", "count": 0},
    {"user":"githublover014", "password": "qwe123456", "count": 0},
    {"user":"githublover015", "password": "qwe123456", "count": 0},
    {"user":"githublover016", "password": "qwe123456", "count": 0},
    {"user":"githublover017", "password": "qwe123456", "count": 0},
    {"user":"githublover018", "password": "qwe123456", "count": 0},
    {"user":"githublover019", "password": "qwe123456", "count": 0},
    {"user":"githublover020", "password": "qwe123456", "count": 0},
    {"user":"githublover021", "password": "qwe123456", "count": 0},
    {"user":"githublover022", "password": "qwe123456", "count": 0},
    {"user":"githublover023", "password": "qwe123456", "count": 0},
    {"user":"githublover024", "password": "qwe123456", "count": 0},
    {"user":"githublover025", "password": "qwe123456", "count": 0},
    {"user":"githublover026", "password": "qwe123456", "count": 0},
    {"user":"githublover027", "password": "qwe123456", "count": 0},
    {"user":"githublover028", "password": "qwe123456", "count": 0},
    {"user":"githublover029", "password": "qwe123456", "count": 0},
    {"user":"githublover030", "password": "qwe123456", "count": 0},
    {"user":"githublover031", "password": "qwe123456", "count": 0},
    {"user":"githublover032", "password": "qwe123456", "count": 0}
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

    
def upload_user_followers(db, user_login):
    need_update = 0
# old res is in our db
    old_res = db["followers"].find_one({"login": user_login})
    if old_res:
        count = user_followers_count(db, user_login)
        old_res_len = len(old_res["followers"])
#for followers more than 500, seems their followers changed very frequently...god
        if (count == old_res_len): 
            print "saved"
#if saved, we could/update all his/her followers
#In the future, we will not upload in this case
#for now, we open it to get more followers info
            in_long_run = 1
            if in_long_run:
                for item in old_res["followers"]:
                    upload_user_followers(db, item["login"])
            return
        else:
# Check if we need to upload
# TODO  better one
            print "user count " + str(count) +"\t follower saved " + str(old_res_len)
            need_update = 1

# new res is updated by calling api
    new_res = user_followers_list(db, user_login)
    if need_update == 0:
        val = {"login": user_login, 
               "followers": new_res,
               "update_date": datetime.datetime.utcnow()
              }
        db["followers"].insert(val)
        print "insert " + user_login
    else:
        val = {"$set": {"update_date": datetime.datetime.utcnow(),
                        "followers": new_res}}
        db["followers"].update({"login":user_login}, val)
        print "update " + user_login

    for item in new_res:
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



class myThread (threading.Thread):
    def __init__(self, db, login):
        threading.Thread.__init__(self)
        self.db = db
        self.login = login
    def run(self):
        print "Starting " + self.login
        upload_user_followers(self.db, self.login)
        print "Exiting " + self.login

def run_task():
    for item in user_thread:
        item.start()


def main():
    exitFlag = 0
    db = init_db()
    for item in init_user:
        new_thread = myThread(db, item)
        user_thread.append(new_thread)

    run_task()

main()


