import base64
import json
import re
import sys
sys.path.append("../../..")
from os import walk
import pymongo
from pymongo import MongoClient

from GithubUser.DMLib.DMDatabase import DMDatabase

def active_user(db):
    active_date_strs = ["^2014", "^2015"]
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
        count = db["chinese"].find(val).count()

#TODO make it a lib
        old_res = db["research_result"].find_one({"type": "chinese_active_count"})
        if old_res:
            db["research_result"].update({"type": "chinese_active_count"}, {"$set": {"total_count": count}})
        else:
            db["research_result"].insert({"type": "chinese_active_count", "total_count": count})
    else:
        print "Cannot connect to database"

main()
