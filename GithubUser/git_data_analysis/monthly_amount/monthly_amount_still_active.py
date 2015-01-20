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
          
# month_str is something like 2010-04
# since I did not change the date from 'string' to 'date'
# I have to use the string compare one..

def find_by_month (db, month_str):
# FIXME: regex seems very very slow
    print "start to find " + month_str
    query_str = '^'+month_str
#    regex = re.compile(query_str)
#    query_json = {"created_at": regex}
    active_date_strs = ["^2014-10", "^2014-11", "^2014-12", "^2015-01"]
    active_query_str = ''
    for item in active_date_strs:
        if len(active_query_str)<1:
            active_query_str = item
        else:
            active_query_str = active_query_str + '|' + item

    created_query_json = {"created_at": {"$regex": query_str}}
    updated_query_json = {"updated_at": {"$regex": active_query_str}}
    query_json = {"$and": [updated_query_json, created_query_json]}

# id ascending is equal to date ascending
# TODO: is it faster? with 3 call, 2 of them is with limit?
    res = db["user"].find(query_json).sort("id", pymongo.ASCENDING)
    res_len = res.count()
    answer = {"type": "monthly_amount_still_alive", 
              "month": month_str,
              "total_public": res_len,
              "update_date": datetime.datetime.utcnow()
             }
    if res_len > 0:
        res_first = res[0]
        res_last = res[res_len-1]
        answer["first"] = {"id": res_first["id"], "login": res_first["login"]}
        answer["last"] = {"id": res_last["id"], "login": res_last["login"]}
    print "\n----------------------\nMonth " + month_str
    print answer
    print   "----------------------\n"

    need_update = 0
    saved_res = db["research_result"].find_one({"type": "monthly_amount_still_alive", "month": month_str})
    if saved_res:
# most time it is right. only if github close/private lots of previous account in a short time
        if saved_res["total_public"] < res_len:
            need_update = 1
        else:
            print "The " + month_str + " result is saved already"
            return

    if need_update:
        db["research_result"].update({"type":"monthly_amount_still_alive", "month": month_str}, {"$set": answer})
        print "The " + month_str + " result is updated"
    else:
        db["research_result"].insert(answer)
        print "The " + month_str + " result is added"

    return

#begin at 2007-10, end at 2015-01
def calculate_months(db):
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
            month_str = "%d-%02d"%(year, month)
            find_by_month(db, month_str)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        calculate_months(db)
    else:
        print "Cannot connect to database"

main()
