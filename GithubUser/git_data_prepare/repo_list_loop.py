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
def append_repos(gh_user_id, page):
    url = "https://api.github.com/users/"+gh_user_id+"/repos?page="+str(page);

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
# We save all the content ... 
# TODO some info is useless actually...
        ret_val.append (item)
    return ret_val

def user_repos_count(db, user_login):
    dc = db["user"]
    result = dc.find_one({"login": user_login})
    if (result):
        return result["public_repos"]
    else:
        return -1

    
def upload_user_repos(db, user_login):
    need_update = 0
# old res is in our db
    old_res = db["repos"].find_one({"login": user_login})
    if old_res:
        count = user_repos_count(db, user_login)
        old_res_len = len(old_res["repos"])
#since it is just init script used for research
#we did the following judgement
#in some of my cases, the user_id is not saved to our 'user' db
#so the old_res_len is 0, in this case, we should update the 'follower' 
        if (old_res_len > 0) and (count <= old_res_len): 
            print "saved"
        else:
# Check if we need to upload
# TODO  better one
            print "user count " + str(count) +"\t follower saved " + str(old_res_len)
            need_update = 1

# new res is updated by calling api
# TODO chould be improved since the 'count' is already got
# use the {} val is better

    new_res = user_repos_list(db, user_login)
    if need_update == 0:
        val = {"login": user_login, 
               "public_repos": len(new_res),
               "repos_info": new_res,
               "update_date": datetime.datetime.utcnow()
              }
        db["repos"].insert(val)
        print "insert " + user_login
    else:
        val = {"$set": {"update_date": datetime.datetime.utcnow(),
                        "public_repos": len(new_res),
                        "repos_info": new_res}}
        db["repos"].update({"login":user_login}, val)
        print "update " + user_login

def user_repos_list(db, user_login):
    res = []
    count = user_repos_count(db, user_login)
    if count <= 0:
        return res
# 30 is github system defined
    page_size = 30
    pages = count/30 + 1
    i = 1
    while i <= pages:
        ret_val = append_repos(user_login, i)
        res += ret_val
        i += 1

    return res



class myThread (threading.Thread):
    def __init__(self, db, start_id, end_id):
        threading.Thread.__init__(self)
        self.db = db
        self.start_id = start_id
        self.end_id = end_id
    def run(self):
        print "Starting " + str(self.start_id)
        i = self.start_id
        while i < self.end_id:
            dc = self.db["user"]
            result = dc.find_one({"id": i})
            if result:
                upload_user_repos(self.db, result["login"])
            i += 1
        print "Exiting " + str(self.start_id)

def run_task():
    for item in user_thread:
        item.start()


def main():
    db = init_db()
    if db:
        #githublover001
        total = 10293416
        thread_num = 64
        gap = total/thread_num
        for i in range(0, thread_num):
            start_id = i * gap
            if i == (thread_num - 1):
                end_id = total
            else:
                end_id = (i+1) * gap
            new_thread = myThread(db, start_id, end_id)
            user_thread.append(new_thread)
        run_task()

main()


