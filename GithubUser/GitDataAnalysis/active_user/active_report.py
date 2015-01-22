import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient

from GithubUser.DMLib.DMDatabase import DMDatabase

# The first user is mojombo, id == 1, created: 2007-10-20

# The very late one is githublover001 id == 10293416 updated: 2015-01-06
          
def report_active(db, type_name):
    saved_res = db["research_result"].find_one({"type": type_name})
    if saved_res:
        print saved_res
    else:
        return

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        report_active(db, "active_count")
        report_active(db, "active_count_3_month")
    else:
        print "Cannot connect to database"

main()
