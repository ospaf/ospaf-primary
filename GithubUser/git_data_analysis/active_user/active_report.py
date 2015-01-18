import base64
import json
import re
import sys
import datetime
import pymongo
from pymongo import MongoClient

# The first user is mojombo, id == 1, created: 2007-10-20

# The very late one is githublover001 id == 10293416 updated: 2015-01-06
          

def init_db ():
    _db_addr = "127.0.0.1"
    _db_port = 27017
    _db_name = "github"

    client = MongoClient(_db_addr, _db_port)
    return client[_db_name]

def report_active(db):
    saved_res = db["research_result"].find_one({"type": "active_count"})
    if saved_res:
        print saved_res
    else:
        return

def main ():
    db = init_db()
    if (db):
        report_active(db)
    else:
        print "Cannot connect to database"

main()
