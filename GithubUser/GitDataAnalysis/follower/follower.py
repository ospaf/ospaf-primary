import base64
import json
import re
import sys
sys.path.append("../../..")
import datetime
import pymongo
from pymongo import MongoClient

from GithubUser.DMLib.DMDatabase import DMDatabase
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers

import followers

def date_string_to_int(date_string):
    num = int(date_string[0:4])*10000+int(date_string[5:7])*100+int(date_string[8:10])
    return num

def addOneUser(db, gh_user_login):
    url = "https://api.github.com/users/"+gh_user_login
    ret_val = DMSharedUsers().readURL(url, {})
    if ret_val["error"] == 1:
        return
    else:
        val = ret_val["val"]
        val["update_date"] = datetime.datetime.utcnow()
        created_at_string = val["created_at"]
        updated_at_string = val["updated_at"]
        created_at_int = date_string_to_int(created_at_string)
        updated_at_int = date_string_to_int(updated_at_string)
        val["created_at_int"] = created_at_int
        val["updated_at_int"] = updated_at_int
        if db["user"].find_one({"login": gh_user_login}):
            db["user"].update({"login": gh_user_login}, {"$set": val})
        else:
            db["user"].insert(val)

beginner = None

def init_beginer(client, login, level):
    global beginner
    beginner = login

    add_to_whole_list(client, login, level)
    add_to_social_level(client, {"level": level, "logins": [login]})

def add_to_social_level(client, item):
    global beginner
    beginner_meta = beginner + "_meta"
    res = client["followers_research"][beginner_meta].find_one({"level": item["level"]})
    if res:
        return 0
    else:
        client["followers_research"][beginner_meta].insert(item)

def add_to_whole_list(client, login, level):
    global beginner
    res = client["followers_research"][beginner].find_one({"login": login})
    if res:
        if res["level"] < level:
        #already added
            return 1
        else:
        #just continue to do the loop
            return 2
    else:
        client["followers_research"][beginner].insert({"login": login, "level": level})
        return 0

def get_follower (db, login):
    res = db.followers.find_one({"login": login})
    if res is None:
        user = db.user.find_one({"login": login})
        if user is None:
            print "User " + login + " even not exist, added"
            addOneUser(db, login)
            user = db.user.find_one({"login": login})
        if user and user["followers"]>0:    
            print "followers " + login + " even not exist, added"
            followers.single_download_demo(user["login"], user["id"], user["followers"])
            res = db.followers.find_one({"login": login})

    if res:
        return res["followers"]
    else:
        print "Cannot get followers of " + login
        return []

def get_followers(client, db, level):
    global beginner
   
    #to continue to do the search work.
    beginner_meta = beginner + "_meta"
    res = client["followers_research"][beginner_meta].find_one({"level": level})
    if res:
        return 1
    print "Start to get level: " + str(level)
    already_count = 0
    new_count = 0
    res = client["followers_research"][beginner].find({"level": level-1})
    for item in res:
        followers = get_follower(db, item["login"])
        #if null, means he/she has no followers..
        for follower in followers:
            val = add_to_whole_list(client, follower["login"], level)
            # 0 means already exist
            if val == 0:
                new_count += 1
            elif val == 1:
                already_count += 1
            else:
                pass
    print str(new_count) + "  new logins added in " + str(level) + "  already added " + str(already_count)
    add_to_social_level(client, {"level": level, "already_count": already_count, "new_count": new_count})

    if new_count > 0:
        return 1
    else:
        return 0

def main ():
    dm_db = DMDatabase()
    client = dm_db.getClient()
    db = dm_db.getDB()
    if (client):
        login = "initlove"
        init_beginer(client, login, 0)
        for level in range (1, 10):
            if get_followers(client, db, level) == 0:
                print "No more, exit"
                break
    else:
        print "Cannot connect to database"

#I have to do this, since some 'bad' people who has name with non-ascii char
#UnicodeEncodeError: 'ascii' codec can't encode character u'\u0107' in position 13: ordinal not in range(128)
reload(sys) 
sys.setdefaultencoding('utf-8')
main()
