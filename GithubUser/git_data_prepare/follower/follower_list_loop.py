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

    
def upload_user_followers(db, user_login, count):
    need_update = 1
# old res is in our db
    old_res = db["followers"].find_one({"login": user_login})
    if old_res:
        if old_res.has_key("count"):
            old_res_len = old_res["count"]
            if (old_res_len > 0) and (count <= old_res_len): 
                print "saved"
                return
        else:
            old_res_len = len(old_res["followers"])
            if (old_res_len > 0) and (count <= old_res_len): 
                print "saved, but need to update - add count prop"
                val = {"$set": {"count": old_res_len}}
                db["followers"].update({"login":user_login}, val)
                return
    else:
        need_update = 0

# new res is updated by calling api
# TODO could be improved since the 'count' is already got
# use the {} val is better

    new_res = user_followers_list(db, user_login)
    new_res_count = len(new_res)
    if need_update == 0:
        val = {"login": user_login, 
               "followers": new_res,
               "count": new_res_count,
               "update_date": datetime.datetime.utcnow()
              }
        db["followers"].insert(val)
        print "insert " + user_login
    else:
        val = {"$set": {"update_date": datetime.datetime.utcnow(),
                        "count": new_res_count,
                        "followers": new_res}}
        db["followers"].update({"login":user_login}, val)
        print "update " + user_login

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
    def __init__(self, db, task):
        threading.Thread.__init__(self)
        saved_task = DMTask().getTask("github", task)
        self.db = db
        if saved_task:
            self.task = saved_task
        else:
            task["status"] = "init"
            self.task = task
            DMTask().addTask("github", self.task)

    def run(self):
        if self.task["status"] == "finish":
            print "Task already finish, exiting the thread"
            return
        else:
            self.task["status"] = "running"
            DMTask().updateTask("github", self.task, {"status": "running"})

        start_id = self.task["start"]
        end_id = self.task["end"]
        if self.task.has_key("current"):
            start_id = self.task["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        query = {"$and": [{"id": {"$gte": start_id, "$lt": end_id}}, {"followers": {"$gt": 0}}]}
        
        dc = self.db["user"]
        res = dc.find(query).sort("id", pymongo.ASCENDING)
        i = 0
        res_len = res.count()
        for item in res:
            f_count = item["followers"]
            upload_user_followers(self.db, res["login"], f_count)
            i += 1
#save every 100 calculate 
            if i%100 == 0:
                if end_id <= start_id:
# This should be checked in DMTask
                    print "Error in the task"
                    return
                percent = 1.0 * i / res_len
                DMTask().updateTask("github", self.task, {"current": res["id"], "percent": percent})

        self.task["status"] = "finish"
        DMTask().updateTask("github", self.task, {"status": "finish"})
        print "Task finish, exiting the thread"

def run_task():
    for item in user_thread:
        item.start()


def main():
    db = DMDatabase().getDB()
    if db:
        total = 10490000
        gap_num = 10000
        thread_num = 64
        for i in range(0, thread_num):
            start_id = i * gap_num
            end_id = (i+1) * gap_num
            task = {"name": "get_followers", "action_type": "loop", "start": start_id, "end": end_id}
            new_thread = myThread(db, task)
            user_thread.append(new_thread)
        run_task()

main()


