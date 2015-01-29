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

class GithubEvent:
    def __init__(self, task):
        self.task = task
        self.db = DMDatabase().getDB()

    def append_event(self, gh_user_id, page):
        url = "https://api.github.com/users/"+gh_user_id+"/events?page="+str(page);
        return DMSharedUsers().readURL(url)

# add a user id is better way to split the event work ..
    def upload_user_event(self, user_login, user_id):
        need_update = 0
        old_res = self.db["event"].find_one({"login": user_login})
        if old_res:
            if old_res.has_key("id"):
                return 0
            else:
# it is a patch .. because we don't save id earlier ..
                self.db["event"].update({"login": user_login}, {"$set": {"id": user_id}})
                return 0

        new_res = self.user_event_list(user_login)
        if (new_res["error"] == 1):
#TODO we should save this error in order to do it again!
            return 1

        count = len(new_res["val"])

        if count > 0:
            print user_login + " added with " + str(count) + " counts"
        self.db["event"].insert({"login": user_login, "id": user_id, "event": new_res["val"], "count": count, "update_date": datetime.datetime.utcnow()})
        return 0

    def user_event_list(self, user_login):
        res = []
        i = 1
        while 1:
            ret_val = self.append_event(user_login, i)
            if ret_val["error"] == 1:
                if i > 2:
#   "message": "In order to keep the API fast for everyone, pagination is limited for this resource. Check the rel=last link relation in the Link response header to see how far back you can traverse.",
#  "documentation_url": "https://developer.github.com/v3/#pagination"
                    return {"error": 0, "val": res}
                else:
                    return {"error": 1}
            if len(ret_val["val"]) > 0:
                orig_size = len(repr(res))
                new_size = len(repr(ret_val["val"]))
#FIXME: gsingharoy, bad people! why will you use such a long message :)
#DocumentTooLarge: BSON document too large (22093046 bytes) - the connected server supports BSON document sizes up to 16777216 bytes.
                if (orig_size + new_size > 16000000):
                    break
                res += ret_val["val"]
                if len(ret_val["val"]) < 30:
                    break
            else:
                break
            i += 1
# simply return if event > 10..
            if i > 10:
                break

        return {"error": 0, "val": res}

    def validateTask(self):
        info = self.task.getInfo()
        if info["start"] > info["end"]:
            print "Error in the task"
            return 0
        return 1

# in case same client cannot access our db
# we give them the logins and get json plain file in return
    def generateToFile(self, output_file):
        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]
        if info.has_key("current"):
            start_id = info["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["user"].find(query).sort("id", pymongo.ASCENDING)
        res_len = res.count()
        i = 0
        fw = open(output_file, "w")
        for item in res:
            fw.write(item["login"])
            fw.write("\n")

    def runTaskFromFile(self, input_file):
        if self.validateTask() == 0:
            return
        if self.task.updateStatus("running") != 0:
            return
        print "import " + input_file
        fo = open(input_file, "r")
        content = fo.read()
        fo.close()
        content_len = len(content)
        val = {}
        if content[content_len-1] == ']':
            val = json.loads(content)
        else:
#Dirty.. yes 
            val = json.loads(content+']')
        for item in val:
            res = self.db["event"].find_one({"login": item["login"]})
            if res:
#TODO compare by the updatetime to make sure if we need to update or just skip it
                self.db["event"].update({"login": item["login"]}, {"$set": item}) 
            else:
                self.db["event"].insert(item)
#TODO we need to verify it since we are not sure if all the data were OK
        print "Task data imported but not finish, exiting the thread"

#task is the instance of DMTask
    def runTask(self):
        if self.validateTask() == 0:
            return
        if self.task.updateStatus("running") != 0:
            return

        info = self.task.getInfo()
        start_id = info["start"]
        end_id = info["end"]
        if info.has_key("current"):
            start_id = info["current"]
            print "Find unfinished task, continue to work at " + str(start_id)

        query = {"id": {"$gte": start_id, "$lt": end_id}}

        res = self.db["user"].find(query).sort("id", pymongo.ASCENDING)
# When the upload takes too long, the cursor will miss
#    cursor.addOption(Bytes.QUERYOPTION_NOTIMEOUT)
# CursorNotFound: cursor id '116709267398' not valid at server
# I should save the id list first
        res_list = []
        for item in res:
            res_list.append({"login": item["login"], "id": item["id"], "updated_at_int": item["updated_at_int"]})
        res_len = len(res_list)
        i = 0
        percent_gap = res_len/100

        for item in res_list:
            updated_date_int = item["updated_at_int"]
            i += 1
            if updated_date_int < 20141000:
                continue 
            ret = self.upload_user_event(item["login"], item["id"])
            if ret == 1:
#TODO make a better error message
                self.task.error({"login": item["login"], "id": item["id"], "message": "error in upload_user_event"})
                continue

            if percent_gap == 0:
                percent = 1.0 * i / res_len
                self.task.update({"current": item["id"], "percent": percent, "update_date": datetime.datetime.utcnow()})
#save every 100 calculate 
            elif i%percent_gap == 0:
                percent = 1.0 * i / res_len
                self.task.update({"current": item["id"], "percent": percent, "update_date": datetime.datetime.utcnow()})

        self.task.update({"status": "finish", "current": end_id, "percent": 1.0, "update_date": datetime.datetime.utcnow()})
        print "Task finish, exiting the thread"

#return the solved errors
    def error_check (self):
        info = self.task.getInfo()
        if info["status"] != "finish":
            return 0

        count = 0
        if info.has_key("error"):
            if info["error_count"] < 10:
                return 0
            update_error = []
            list = info["error"]
            for item in list:
                login = item["login"]
                if self.db["event"].find_one({"login": login}):
                    count += 1
                    continue
                id = 0
                if item.has_key("id"):
                    id = item["id"] 
                else:
                    user_res = self.db["user"].find_one({"login": login})
                    if user_res:
                        id = user_res["id"]
                    else:
                        continue
                ret = self.upload_user_event(login, id)
# error
                if ret == 1:
                    update_error.append({"login": login, "id": id, "message": "error even in double upload_user_event"})
                else:
                    count += 1
            error_len = len(update_error)
            self.task.update({"error": update_error, "error_count": error_len})
        return count

def resolve_event_errors():
    gap = 1000
    start = 0
# end id is now set to 10300000
    end = 10300  
    count = 0
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_events", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r = GithubEvent(task)
        res = r.error_check()
        count += res
    print str(count) + " errors solved"

# very important, the entry function
def init_event_task():
# TODO: 1000 is system defined, maybe add to DMTask? or config file?
    gap = 1000
    start = 0
# end id is now set to 10300000
    end = 10300  
    db = DMDatabase().getDB()
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_events", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)

#easier for developing - than 'fix_add_login'
def fix_add_created_at_int():
    db = DMDatabase().getDB()
#2730627
    gap = 1000
    start = 3000
# end id is now set to 10300000
    end = 9000  

    for i in range(start, end):
        res = db["user"].find({"id": {"$gte": i * gap, "$lt": (i+1)*gap}})
        for item in res:
            db["event"].update({"login": item["login"]}, {"$set": {"created_at_int": item["created_at_int"]}})
        print i
        

def fix_add_login():
    db = DMDatabase().getDB()
#2730627
    gap = 100
    num = 0

    while 1:
        print 'begin'
        res =db["event"].find({"id": {"$exists": False}}).limit(gap)
        print 'end'
        if res:
            print res.count()
            if res.count() == 0:
                return 
            for item in res:
                num += 1
                login = item["login"]
                user_item = db["user"].find_one({"login": login})
                db["event"].update({"login": login}, {"$set": {"id": user_item["id"]}})
        else:
            print 'exit'
            return
        print num

# since I find each 1000 - id task only get less than 200 event records.. so I need to double check
def check_task(task):
    db = DMDatabase().getDB()
    count1 = db["user"].find({"id": {"$gte": task["start"], "$lt": task["end"]}, "updated_at_int": {"$gte": 20141000}}).count()
    count2 = db["event"].find({"id": {"$gte": task["start"], "$lt": task["end"]}}).count()
    print str(count1) + ' in user and ' + str(count2) + ' in event'

def test():
    db = DMDatabase().getDB()
    res = db["event"].find({"id": {"$gte": 1000, "$lt": 200}}).limit(20)
    if res is None:
        print 'res is none'
    else:
        print res.count()
    return

    task1 = DMTask()
    val = {"name": "fake-event", "action_type": "loop", "start": 6001000, "end": 6005000}

    task1.init_test("github", val)
    e1 = GithubEvent(task1)
    e1.runTask()
    task1.remove()

#init_event_task()

#test()

#resolve_event_errors()
#fix_add_login()

#so far, the check_task is write..
#check_task({"start": 3888000, "end": 3889000})
#check_task({"start": 4512000, "end": 4513000})

#fix_add_created_at_int()
