import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase

def fork_org(db, num):
    item = db["research_result"].find_one({"type": "get_fork_more_than_num_org_count", "num": num})
    if item:
        print "Already exist"
        print item
        return

    alive = db["repositories"].find({"forks_count": {"$gte": num}, "owner.type": "Organization", "updated_at_int": {"$gte": 20141000}}).count()
    count = db["repositories"].find({"forks_count": {"$gte": num}, "owner.type": "Organization"}).count()
    whole = db["repositories"].find({"forks_count": {"$gte": num}}).count()
    db["research_result"].insert({"type": "get_fork_more_than_num_org_count", "num": num, "alive": alive, "count": count, "whole": whole})
    print str(count) + "  orgs in all the " + str(whole) + " whoes fork is more than " + str(num)

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        nums = [100, 200, 1000, 10, 50]
        for num in nums:
            fork_org(db, num)
        print "Cannot connect to database"

main()
