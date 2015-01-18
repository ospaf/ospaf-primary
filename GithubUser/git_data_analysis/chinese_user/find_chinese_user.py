import base64
import json
import re
import sys
from os import walk
import pymongo
from pymongo import MongoClient

def init_db ():
    _db_addr = "127.0.0.1"
    _db_port = 27017
    _db_name = "github"
    _db_collection = "user"

    client = MongoClient(_db_addr, _db_port)
    db = client[_db_name]
    return db

def read_china_conf ():
    special_file = ["location", "company", "login", "name", "email"]
    conf_db = []
    for item in special_file:
        fo = open("./conf/"+item)
        item_list = []
        for line in fo.readlines():
            line = line.strip()
            if not len(line):
                continue
            elif line.startswith('#'):
                continue
            else:
                item_list.append(line)
        conf_db.append({"name": item, "value": item_list})
    return conf_db
    
def reg_china_condition ():
    conf_db = read_china_conf()
    or_list = []
    for item in conf_db:
        str = ''
        for item_value in item["value"]:
            if len(str) == 0:
                str = item_value
            else:
                str = str + '|' + item_value
        item_regex = re.compile(str, re.IGNORECASE)
        or_list.append({item["name"]: item_regex})
    or_con = {"$or": or_list}
    res = or_con
    return res

def add_chinese(db, item):
    old_res = db["chinese"].find_one({"id": item["id"]})
    if old_res:
        return

    props = ["id", "login", "name", "location", "blog", "email", "type",
            "public_repos", "public_gists", "followers", "following", 
            "created_at", "updated_at"]
    res = {}
    for prop in props:
        if item.has_key(prop):
            res[prop] = item[prop]
    db["chinese"].insert(res)

def main ():
    db = init_db()
    if (db):
        val = reg_china_condition()
        result = db["user"].find(val)
        count = 0
        for item in result:
            count += 1
            add_chinese(db, item)
            if count%500 == 0:
                print count

#TODO make it a lib
        old_res = db["research_result"].find_one({"type": "chinese_count"})
        if old_res and old_res["total_count"] != count:
            db["research_result"].update({"$set": {"total_count": count}})
        else:
            db["research_result"].insert({"type": "chinese_count", "total_count": count})
    else:
        print "Cannot connect to database"

main()
