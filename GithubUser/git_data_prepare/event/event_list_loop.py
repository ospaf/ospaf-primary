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

user_thread = []

# In github - follower, the default page_size is 30 and we cannot change it. 
#    seems...Correct me if I were wrong
def append_event(gh_user_id, page):
    url = "https://api.github.com/users/"+gh_user_id+"/events?page="+str(page);
#    print url
    req = urllib2.Request(url)
    fu = DMSharedUsers().getFreeUser()
    base64string = base64.encodestring('%s:%s' % (fu["login"], fu["password"])).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)   

    try:
        res_data = urllib2.urlopen(req)
    except urllib2.URLError, err:
# TODO we should note this ...
        print 'dliang url error' + url
        print err
        return {"error": 1}
    except urllib2.HTTPError, err:
        print '404 error'
        if err.code == 404:
             return {"error": 1}
    except httplib.HTTPException, err:
        print 'http exception'
        return {"error": 1}
# TODO timeout
    else:
        res = res_data.read()
        val = json.loads(res)
        return {"error": 0, "val": val}

    print "How to get here?"
    return {"error": 1}

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
#FIXME: what if we received page1 and get error in page2
        if (ret_val["error"] == 1):
            return {"error":1}
        elif len(ret_val["val"]) == 0:
            break
        res += ret_val["val"]
        i += 1

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
                updated_date = result["updated_at"]
                if active_date(updated_date):
                    upload_user_event(self.db, result["login"])
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
        print gap

        for i in range(0, thread_num):
            start_id = i * gap + 60000
            if i == (thread_num - 1):
                end_id = total
            else:
                end_id = (i+1) * gap
            new_thread = myThread(db, start_id, end_id)
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


