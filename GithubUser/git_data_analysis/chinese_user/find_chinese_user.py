import base64
import json
import re
import sys
from os import walk
import pymongo
from pymongo import MongoClient

def init_db ():
    _db_addr = "147.2.207.55"
    _db_port = 27017
    _db_name = "github"
    _db_collection = "user"

    client = MongoClient(_db_addr, _db_port)
    dc = client[_db_name][_db_collection]
    return dc

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

def main ():
    dc = init_db()
    if (dc):
        val = reg_china_condition()
        result = dc.find(val)
        print result.count()
    else:
        print "Cannot connect to database"

main()
