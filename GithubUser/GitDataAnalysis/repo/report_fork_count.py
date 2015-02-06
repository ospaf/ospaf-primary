import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase

def report_forks(db, num):
    c1 = db["repositories"].find({"fork": false, "forks_count": num}}).count()
    c2 = db["repositories"].find({"fork": true, "forks_count": num}}).count()
    print "fork false count " + str(c1) + "  fork true count " + str(c2)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        for num in range(0, 10):
            report_forks(db, num)
    else:
        print "Cannot connect to database"

main()
