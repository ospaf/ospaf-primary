import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase

hot_langs = ["JavaScript", "Java", "Ruby", "Python", "PHP", "CSS", "C", 
 "C++", "Objective-C", "C#", "Shell", "Perl", "R", "Go"]

def report_lang(db):
    res = db["research_result"].find({"type": "get_lang_count"})
    other_count = 0
    count = 0
    for item in res:
        count += item["count"]
        if item["name"] in hot_langs:
            print item["name"] + "\t" + str(item["count"])
        else:
            other_count += item["count"]

    print "Total " + str(count)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        report_lang(db)
    else:
        print "Cannot connect to database"

main()
