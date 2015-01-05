import base64
import json
import re

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

def reg_condition ():
    conf_db = [{"name": "location", "value": ["china", "chinese", "peking", "chengdu"]},
               {"name": "company", "value": ["china", "chinese", "peking", "chengdu"]},
               {"name": "login", "value": ["liang", "wang", "chen", "xiong", "liu", "zhang", "wong", "zhou", "jiang"]},
               {"name": "name", "value": ["liang", "wang", "chen", "xiong", "liu", "zhang", "wong", "zhou", "jiang"]},
               {"name": "email", "value": ["qq.com", "163.com", "sina.com", "sohu.com"]}
              ]
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
    if (dc) :
        str = "china|chinese"
        reg = re.compile(str, re.IGNORECASE)
        loc1 = {"location": reg}
        location01 = "location"
        val = {"$or": [{location01: reg}]}
        val = reg_condition()
        result = dc.find(val)
        print result.count()

main()

