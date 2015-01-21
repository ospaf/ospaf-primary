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
          
# month_str is something like 201004
def report_by_month (db, month_int):
    saved_res = db["research_result"].find_one({"type": "monthly_amount_still_active", "month": month_int})
    if saved_res:
        gap = 0
        print str(month_int) + "\t" + str(saved_res["total_public"])
    else:
        return

#begin at 2007-10, end at 2015-01
def report_months(db):
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
            month_int = year*100 + month
            report_by_month(db, month_int)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        report_months(db)
    else:
        print "Cannot connect to database"

main()
