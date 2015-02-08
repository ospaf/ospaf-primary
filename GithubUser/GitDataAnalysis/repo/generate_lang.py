import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase

def generate_lang(db, lan):
    count = db["repositories"].find({"language": lan}).count()
    print lan + "  " + str(count)
    db["research_result"].insert({"type": "get_lang_count", "name": lan, "count": count})

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        fo = open("./lang.txt", "r")
        for line in fo.readlines():
            line = line.strip()
            if not len(line) or line.startswith('#'):
                continue
            else:
                generate_lang(db, line)
    else:
        print "Cannot connect to database"

main()
