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
whole_followers = []
social = []

def init_beginer(login):
    global beginner
    global whole_followers
    global social
    beginner = login
    whole_followers.append(login)
    social.append({"level": 0, "logins": [login]})

def add_to_whole_list(login):
    for item in whole_followers:
        if item == login:
            return 0
    whole_followers.append(login)
    return 1

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
    global whole_followers
    global social
    res = client["followers_research"][beginner].find_one({"level": level+1})
    if res:
        for follower in res["logins"]:
            add_to_whole_list(follower["login"])
        print "Already in db, " + str(len(res["logins"])) + "  counts"
        social.append({"level": level+1, "logins": res["logins"]})
        return

    new_logins = []
    already_count = 0
    for item in social:
        if item["level"] == level:
            logins = item["logins"]
            for login in logins:
                followers = get_follower(db, login)
                #if null, means he/she has no followers..
                for follower in followers:
                    val = add_to_whole_list(follower["login"])
                    # 0 means already exist
                    if val == 0:
                        already_count += 1
                        pass
                    else:
                        new_logins.append(follower["login"])
        else:
            pass
    count = len(new_logins)
    print str(count) + "  new logins added in " + str(level) + "  already added " + str(already_count)
    social.append({"level": level+1, "logins": new_logins})

    client["followers_research"][beginner].insert({"level": level+1, "logins": new_logins})
    if count > 0:
        return 1
    else:
        return 0

def main ():
    dm_db = DMDatabase()
    client = dm_db.getClient()
    db = dm_db.getDB()
    if (client):
        login = "initlove"
        init_beginer(login)
        for level in range (0, 10):
            if get_followers(client, db, level) == 0:
                break
    else:
        print "Cannot connect to database"

#I have to do this, since some 'bad' people who has name with non-ascii char
#UnicodeEncodeError: 'ascii' codec can't encode character u'\u0107' in position 13: ordinal not in range(128)
reload(sys) 
sys.setdefaultencoding('utf-8')
main()
