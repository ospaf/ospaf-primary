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

user_thread = []

# In github - event, the default page_size is 30 and we cannot change it. 
#    seems...Correct me if I were wrong
# different with pub_repos or followers, we need to track the error!
def append_event(gh_user_id, page):
    url = "https://api.github.com/users/"+gh_user_id+"/events?page="+str(page);
  
    return DMSharedUsers().readURL(url)

def upload_user_event(db, user_login):
    need_update = 0
# old res is in our db
    old_res = db["event"].find_one({"login": user_login})
    if old_res:
# simply return it!
        return

    new_res = user_event_list(db, user_login)
    if (new_res["error"] == 1):
        return

    count = len(new_res["val"])

    if count > 0:
        print user_login + " added with " + str(count) + " counts"
#TODO add the event count is good for analysis
    db["event"].insert({"login": user_login, "event": new_res["val"], "count": count, "update_date": datetime.datetime.utcnow()})

def user_event_list(db, user_login):
    res = []
# 30 is github system defined
    i = 1
#    print "User event " + user_login + " begin"
    while 1:
        ret_val = append_event(user_login, i)
        if ret_val["error"] == 1:
            if i > 2:
#   "message": "In order to keep the API fast for everyone, pagination is limited for this resource. Check the rel=last link relation in the Link response header to see how far back you can traverse.",
#  "documentation_url": "https://developer.github.com/v3/#pagination"
                return {"error": 0, "val": res}
            else:
                return {"error": 1}
        res += ret_val["val"]
        i += 1
# simply return if event > 10..
        if i > 10:
            break

#    print "User event " + user_login + " end"
    return {"error": 0, "val": res}

def active_date(date):
# github just save the last three month, or we say, last 90 days.
    active_month = ["2014-10", "2014-11", "2014-12", "2015-01"]
    query_str = ''

    for item in active_month:
        if len(query_str) == 0:
            query_str = "^" + item
        else:
            query_str = query_str + "|^" + item
    reg = re.compile(query_str)
    val = reg.search (date)
    if val:
        return 1
    else:
        return 0


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
        if self.task["status"] == "error":
            print "Task error, exiting the thread"
            return
        elif self.task["status"] == "finish":
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

        if end_id <= start_id:
# This should be checked in DMTask
            print "Error in the task"
            return

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["user"].find(query).sort("id", pymongo.ASCENDING)
        res_len = res.count()
        i = 0
        percent_gap = res_len/100
        for item in res:
            updated_date = item["updated_at"]
            i += 1
            if active_date(updated_date):
                upload_user_event(self.db, item["login"])
            if percent_gap == 0:
                percent = 1.0 * i / res_len
                DMTask().updateTask("github", self.task, {"current": item["id"], "percent": percent})
#save every 100 calculate 
            elif i%percent_gap == 0:
                percent = 1.0 * i / res_len
                DMTask().updateTask("github", self.task, {"current": item["id"], "percent": percent})

        self.task["status"] = "finish"
        DMTask().updateTask("github", self.task, {"status": "finish", "current": end_id, "percent": 1.0})
        print "Task finish, exiting the thread"

def run_task():
    for item in user_thread:
        item.start()


def main():
    db = DMDatabase().getDB()
    if db:
        total = 10490000
        gap_num = 10000
        thread_num = 128
        for i in range(0, thread_num):
            start_id = i * gap_num
            end_id = (i+1) * gap_num
            task = {"name": "get_events", "action_type": "loop", "start": start_id, "end": end_id}
            new_thread = myThread(db, task)
            user_thread.append(new_thread)
        run_task()

def fake():
    db = DMDatabase().getDB()
    if db:
        total = 10293416
        thread_num = 64
        gap = total/thread_num
        print gap
        upload_user_event (db, "initlove")

def fix_event():
    db = DMDatabase().getDB()
    res = db["event"].find()
    for item in res:
        count = len(item["event"])
        db["event"].update({"login": item["login"]}, {"$set": {"update_date": datetime.datetime.utcnow(), "count": count}})
    print "Finish"

#seconds
timeout = 60
socket.setdefaulttimeout(timeout)
main()
#fake()


