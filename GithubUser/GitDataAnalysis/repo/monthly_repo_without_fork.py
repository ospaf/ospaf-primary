import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase

# month_str is something like 201004
def report_by_month (db, month_start):
    month_int = month_start/100
    saved_res = db["research_result"].find_one({"type": "monthly_repo_without_fork_amount", "month": month_int})
    need_update = 0
    if saved_res:
        need_update = 1

    month_end = month_start + 100
    query_created = {"fork": False, "created_at_int": {"$gte": month_start, "$lt": month_end}}

    count = db["repositories"].find(query_created).count()
    if need_update:
        db["research_result"].update({"type": "monthly_repo_without_fork_amount", "month": month_int}, {"$set": {"count": count}})
    else:
        db["research_result"].insert({"type": "monthly_repo_without_fork_amount", "month": month_int, "count": count})

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
            month_start = year*10000+month*100
            item = report_by_month(db, month_start)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        report_months(db)
    else:
        print "Cannot connect to database"

main()
