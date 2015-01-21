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

def find_by_month_int (db, month_int_start):
    print "start to find " + str(month_int_start)
    month_int_end = month_int_start + 100
    query_created = {"created_at_int": {"$gte": month_int_start, "$lt": month_int_end}}
    query_updated = {"updated_at_int": {"$gt": 20141000}}
    query_json = {"$and": [query_created, query_updated]}
    res_len = db["user"].find(query_json).count()
    answer = {"type": "monthly_amount_still_active", 
              "month": month_int_start/100,
              "total_public": res_len,
              "update_date": datetime.datetime.utcnow()
             }
    print "\n----------------------\nMonth " + str(month_int_start/100)
    print answer
    print   "----------------------\n"

    need_update = 0
    saved_res = db["research_result"].find_one({"type": "monthly_amount_still_active", "month": month_int_start/100})
    if saved_res:
        need_update = 1

    if need_update:
        db["research_result"].update({"type":"monthly_amount_still_active", "month": month_int_start/100}, {"$set": answer})
        print "The " + str(month_int_start/100) + " result is updated"
    else:
        db["research_result"].insert(answer)
        print "The " + str(month_int_start/100) + " result is added"

    return

#begin at 2007-10, end at 2015-01
def calculate_months_int(db):
    begin_date = {"year": 2007, "month": 10}
    end_date = {"year": 2015, "month": 1}
    for year in range(begin_date["year"], end_date["year"]+1):
        begin_month = 1
        end_month = 12
        if year == begin_date["year"]:
            begin_month = begin_date["month"]
        elif year == end_date["year"]:
            end_month = end_date["month"]

        for month in range(begin_month, end_month+1):
            month_int = year*10000 + month * 100
            find_by_month_int(db, month_int)

#since I convert date string to int
def main_int ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        calculate_months_int(db)
    else:
        print "Cannot connect to database"

main_int()
