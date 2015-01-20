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

def date_string_to_int(date_string):
    num = int(date_string[0:4])*10000+int(date_string[5:7])*100+int(date_string[8:10])
    return num

#This is used to make 'date' related operation faster
def fix_event():
    db = DMDatabase().getDB()
    res = db["user"].find()
    i = 0
    for item in res:
        created_at_string = item["created_at"]
        updated_at_string = item["updated_at"]
        created_at_int = date_string_to_int(created_at_string)
        updated_at_int = date_string_to_int(updated_at_string)

        db["user"].update({"login": item["login"]}, {"$set": {"created_at_int": created_at_int, "updated_at_int": updated_at_int}})
        i += 1
        if i%10000 == 0:
            print i
    print "Finish"

fix_event()

