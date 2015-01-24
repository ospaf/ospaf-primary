import sys
import os
import base64
import json

import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from DMDatabase import DMDatabase

#TODO try catch...
#TODO client could stop the task once it cannot continue and other could do the task for the original client
#       use ping to show the client is alive? or we add a timeout to each task record?

class DMTask:
    __task_client__ = None
    __task_db__ = None
    def __init__(self):
        if DMTask.__task_db__ is not None:
            return
        DMTask.__task_client__ = DMDatabase().getClient()
        DMTask.__task_db__ = DMTask.__task_client__["task"]
        self._id = None

    def init(self, col, task):
        self.col = DMTask.__task_db__[col]
        key_val = {"name": task["name"], "action_type": task["action_type"], "start": task["start"], "end": task["end"]}
        res = self.col.find_one(key_val)
        if res:
            self._id = res["_id"]
            print "use saved task"
        else:
            task["status"] = "init"
            task["percent"] = 0.0
            _id = self.col.insert(task)
            self._id = ObjectId(_id)
            print "new task added"

    def init_test(self, col, task):
        DMTask.__task_db__ = DMTask.__task_client__["test-task"]
        self.col = DMTask.__task_db__[col]
        key_val = {"name": task["name"], "action_type": task["action_type"], "start": task["start"], "end": task["end"]}
        res = self.col.find_one(key_val)
        if res:
            self._id = res["_id"]
            print "use saved task"
        else:
            task["status"] = "init"
            task["percent"] = 0.0
            _id = self.col.insert(task)
            self._id = ObjectId(_id)
            print "new task added"

    def getInfo(self):
        if self._id == None:
            return None
        else:
            return self.col.find_one({"_id": self._id})

# the content of val is client defined
    def error(self, val):
        res = self.col.find_one({"_id": self._id})
        if res:
            error_tasks = []
            if res.has_key("error"):
               error_tasks=res["error"]
            error_tasks.append(val)
            error_task_count = len (error_tasks)
            self.col.update({"_id": self._id}, {"$set": {"error": error_tasks, "error_count": error_task_count}}) 
        
# prefer not to use this ..
    def remove (self):
         self.col.remove({"_id": self._id})

    def update(self, val):
#TODO action type and other key value should not be updated
        self.col.update({"_id": self._id}, {"$set": val})

    def updateStatus (self, status):
        res = self.col.find_one({"_id": self._id})
        if res:
            if res.has_key("status"):
                if res["status"] == "error":
                    print "Task error, exiting the thread"
# TODO define the error code
                    return 1
                elif res["status"] == "finish":
                    print "Task already finish, exiting the thread"
                    return 1
            self.col.update({"_id": self._id}, {"$set": {"status": status}})
            return 0
        else:
            return 1


#TODO connect with server will be better
    def status(self):
        print "TaskInfo: "
        res = self.col.find_one({"_id": self._id})
        if res:
            print res
        else:
            print "Removed, cannot be found"

#---------------- global function -----------------#
    def findTask(self, col, task):
        return DMTask.__task_db__[col].find_one(task)

#TODO: we need to lock or check the real task ...by updatetime?
#num is the tasks each client want to have
    def getFreeTasks(self, req):
#      {"col": "github", 
# we can use num to get max task number
#       "num": num, 
# we can use timeout to check if the client was disconnected
#       "timeout": timeout, 
# we can set own query like special query request, this is could be empty       
#        "query": query}
        query = {}
        if req.has_key("query"):
            query = req["query"]
        else:
            query["status"] = "init"
        return DMTask.__task_db__[req["col"]].find(query).sort("percent", pymongo.ASCENDING).limit(req["num"])

def test1():
    col = "github"
    task1 = {"name": "fake3", "action_type": "loop", "start": 1, "end": 10}
    dm_task1 = DMTask()
    dm_task1.init_test(col, task1)
    dm_task1 = DMTask()
    dm_task1.init_test(col, task1)

    print dm_task1.updateStatus ("init")


    dm_task1.status()
    print dm_task1.updateStatus ("in progress")
    dm_task1.update({"percent" : 0.1})
    dm_task1.error({"login": "fakeuser", "message":"error in test"})
    dm_task1.status()

    res = DMTask().findTask(col, task1)
    print res

    dm_task1.remove()
 
    dm_task1.status()
    res = DMTask().findTask(col, task1)
    print res

def test2():
    col = "github"
    task2 = {"name": "fake3", "action_type": "loop", "start": 1, "end": 10}
    dm_task2 = DMTask()
    dm_task2.init_test(col, task2)

    print "======== free ========"
    res = DMTask().getFreeTasks({"col": col, "num": 5})
    dm_task1 = DMTask()
    for item in res:
        dm_task1.init_test(col, item)
        dm_task1.status()
        break
    
    print "======== free ========"

#test2()
