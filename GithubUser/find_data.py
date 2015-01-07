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

# TODO not really useful now since it could be done easily by using mongo command
def repo_condition(num):
    res = {"public_repos": {"$gte" : num}}
    return res

def followers_get(num):
    res = {"followers": {"$gte" : num}}
    return res

def created_date_count(date):
    str = '^'+date
    regex = re.compile(str)
    res = {"created_at": regex}
    return res

def updated_date_count(date):
    str = '^'+date
    regex = re.compile(str)
    res = {"updated_at": regex}
    return res

def id_count(min, max):
    res = {"id": {"$gte": min, "$lt": max}}
    return res

def command_process (dc, argv):
    command = argv[1]
    if command == "chinese":
        val = reg_china_condition()
        result = dc.find(val)
        print result.count()
    elif command == "repos":
        if len(argv) < 3:
            print "Please input the minim repos"
            return
        else:
            val = repo_condition(long(sys.argv[2]))
            result = dc.find(val)
            print result.count()
            return
    elif command == "created_date":
        if len(argv) < 3:
            print "Please input the date like 2013-03-14"
            return
        else:
            val = created_date_count(sys.argv[2])
            result = dc.find(val)
#print one example
#            if (result > 0):
#                print result[0]
            print result.count()
            return
    elif command == "updated_date":
        if len(argv) < 3:
            print "Please input the date like 2013-03-14"
            return
        else:
            val = updated_date_count(sys.argv[2])
            result = dc.find(val)
#print one example
            if (result > 0):
                print result[0]
                print result.count()
            else:
                print "Empty"
            return
    elif command == "id":
        if len(argv) < 4:
            print "Please input the begin id and end id"
            return
        else:
            val = id_count(long(sys.argv[2]), long(sys.argv[3]))
            result = dc.find(val)
#print one example
            if (result > 0):
                print result[0]
                print result.count()
            else:
                print "Empty"
            return
    elif command == "followers":
        if len(argv) < 3:
            print "Please input the minim followers"
            return
        else:
            val = followers_get(long(sys.argv[2]))
            result = dc.find(val)
#print one example
            if (result > 0):
                for item in result:
                    print item["login"]
                print result.count()
            else:
                print "Empty"
            return
           
    else:
        print "Not implemented yet or wrong command"
        return
    return
        

def main ():
    if len(sys.argv) < 2:
        print "Please enter the command"
        return
    dc = init_db()
    if (dc):
        command_process(dc, sys.argv)
    else:
        print "Cannot connect to database"

main()
