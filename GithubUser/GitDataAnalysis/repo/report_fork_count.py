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
    c1 = db["repositories"].find({"forks_count": num}).count()
    print "fork false count " + str(c1)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        for num in range(0, 76000):
            report_forks(db, num)
    else:
        print "Cannot connect to database"

main()
