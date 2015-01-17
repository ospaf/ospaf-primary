import base64
import json
import re
import sys
from os import walk
import pymongo
from pymongo import MongoClient

def init_db ():
    _db_addr = "147.2.207.55"
    _db_port = 27017
    _db_name = "github"

    client = MongoClient(_db_addr, _db_port)
    db = client[_db_name]
    return db

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
    db = init_db()
    if (db):
        val = active_user(db)
        count = db["chinese"].find(val).count()

#TODO make it a lib
        old_res = db["research_result"].find_one({"type": "chinese_active_count"})
        if old_res and old_res["total_count"] != count:
            db["research_result"].update({"$set": {"total_count": count}})
        else:
            db["research_result"].insert({"type": "chinese_active_count", "total_count": count})
    else:
        print "Cannot connect to database"

main()
