import sys
import os
import base64
import json

import datetime
import pymongo
from pymongo import MongoClient
from DMDatabase import DMDatabase

#TODO try catch...

class DMTask:
    __task_db__ = None
    def __init__(self):
        if DMTask.__task_db__ is not None:
            return
        client = DMDatabase().getClient()
        DMTask.__task_db__ = client["task"]

    def getTask(self, col, task):
#       task = {"name": "get_followers", "action_type": "loop", "start": start_id, "end": end_id}
#       action_type is used for the future ....
# I prefer not to use _id
        key_val = {"name": task["name"], "action_type": task["action_type"], "start": task["start"]}
        return DMTask.__task_db__[col].find_one(key_val)

    def updateTask(self, col, task):
        key_val = {"name": task["name"], "action_type": task["action_type"], "start": task["start"]}
        val = {"$set": task}
        DMTask.__task_db__[col].update(key_val, val)

    def addTask (self, col, task):
        if getTask(self, col, task):
# TODO
            print "The task has already exist, TODO, how to work this situation?"
            return
        else:
            DMTask.__task_db__[col].insert(task)

#TODO connect with server will be better
    def taskStatus(self, col):
        print "AccountInfo: "
        print DMTask.__task_db__[col].find()

