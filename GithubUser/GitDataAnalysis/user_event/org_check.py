import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        res = db["event"].find({"count" : {"$gte": 299}})
        org_count = 0
        for item in res:
            user_item = db["user"].find_one({"id": item["id"]})
            if user_item:
                print user_item["login"]
                if user_item["type"] == "Organization":
                    org_count += 1
        print "Org is " + str(org_count)
    else:
        print "Cannot connect to database"

main()
