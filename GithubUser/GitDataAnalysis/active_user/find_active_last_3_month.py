import base64
import json
import re
import sys
sys.path.append("../../..")
from os import walk
import pymongo
from pymongo import MongoClient

def active_user(db):
    active_date_strs = ["^2014-10", "^2014-11", "^2014-12", "^2015-01"]
    active_query_str = ''
    for item in active_date_strs:
        if len(active_query_str)<1:
            active_query_str = item
        else:
            active_query_str = active_query_str + '|' + item
        
    item_regex = re.compile(active_query_str, re.IGNORECASE)
    res = {"updated_at": item_regex}
    return res
  

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        val = active_user(db)
        count = db["user"].find(val).count()

# .. demo of remove a record
#        db["research_result"].remove({"type": "active_count"})
#TODO make it a lib
        old_res = db["research_result"].find_one({"type": "active_count_3_month"})
        if old_res:
            db["research_result"].update({"type": "active_count_3_month"},{"$set": {"total_count": count}})
        else:
            db["research_result"].insert({"type": "active_count_3_month", "total_count": count})
    else:
        print "Cannot connect to database"

main()
