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

    total = 1050
    gap_num = 10000
    i = 0
    while i<total:
        min = i * gap_num
        max = (i+1) * gap_num
        query = {"id": {"$gte": min, "$lt": max}}

        res = db["user"].find(query)
        for item in res:
            if item.has_key("created_at_int"):
                continue
            created_at_string = item["created_at"]
            updated_at_string = item["updated_at"]
            created_at_int = date_string_to_int(created_at_string)
            updated_at_int = date_string_to_int(updated_at_string)
            db["user"].update({"login": item["login"]}, {"$set": {"created_at_int": created_at_int, "updated_at_int": updated_at_int}})
        i += 1
        print i
    print "Finish"

fix_event()

