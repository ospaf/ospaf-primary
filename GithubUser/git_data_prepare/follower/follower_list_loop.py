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
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers

user_thread = []

# In github - follower, the default page_size is 30 and we cannot change it. 
#    seems...Correct me if I were wrong
def append_followers(gh_user_id, page):
    url = "https://api.github.com/users/"+gh_user_id+"/followers?page="+str(page);
    req = urllib2.Request(url)
    fu = DMSharedUsers().getFreeUser()
    base64string = base64.encodestring('%s:%s' % (fu["login"], fu["password"])).replace('\n', '')
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
#since it is just init script used for research
#we did the following judgement
#in some of my cases, the user_id is not saved to our 'user' db
#so the old_res_len is 0, in this case, we should update the 'follower' 
        if (old_res_len > 0) and (count <= old_res_len): 
            print "saved"
#if saved, we could/update all his/her followers
#In the future, we will not upload in this case
#for now, we open it to get more followers info
            in_long_run = 0
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
# TODO chould be improved since the 'count' is already got
# use the {} val is better

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

    in_long_run = 0
    if in_long_run:
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
                upload_user_followers(self.db, result["login"])
            i += 1
        print "Exiting " + str(self.start_id)

def run_task():
    for item in user_thread:
        item.start()


def main():
    db = DMDatabase().getDB()
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


