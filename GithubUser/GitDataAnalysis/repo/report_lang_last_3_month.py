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
    res = db["research_result"].find({"type": "get_lang_count_last_3_month"})
    other_count = 0
    count = 0
    for item in res:
        count += item["count"]
        if item["name"] in hot_langs:
            per = 100.0 * item["count"] / 11545755
            print str(item["count"]) + "\t" + item["name"] + " ("+ '%3.1f' % per+ "%)"
        else:
            other_count += item["count"]
    per = 100.0 * other_count / 11545755
    print str(item["count"]) + "\t" +  "Other " + " (" + '%3.1f' % per + "%)"
    print "Total " + str(count)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        report_lang(db)
    else:
        print "Cannot connect to database"

main()
