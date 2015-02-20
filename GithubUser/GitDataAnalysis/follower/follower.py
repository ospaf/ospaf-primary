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

whole_followers = ["initlove"]
social = [{"level": 0, "logins": ["initlove"]}]

def add_to_whole_list(login):
    for item in whole_followers:
        if item == login:
            return 0
    whole_followers.append(login)
    return 1

def get_follower (db, login):
    res = db.followers.find_one("login": login)
    if res:
        return res["followers"]
    else:
        print "Cannot get followers of " login
        return []

def get_followers(db, level):
    new_logins = []
    for item in social:
        if item["level"] == level:
            logins = item["logins"]
            for login in logins:
                followers = get_follower(db, login)
                for follower in followers:
                    val = add_to_whole_list(follower["login"])
                    # 0 means already exist
                    if val == 0:
                    else:
                        new_logins.append(follower)
        else:
            pass
    count = len(new_logins)
    print str(count) + "  new logins added in " + len(level)
    social.append({"level": level+1, "logins": new_logins})
    if count > 0:
        return 1
    else:
        return 0

def main ():
    dm_db = DMDatabase()
    client = dm_db.getClient()
    db = dm_db.getDB()
    if (client):
#user name is a database
#repo_name is col to store repos that
#user is another col to store contributors' info
        for level in range (0, 5):
            if get_followers(db, level) == 0:
                break
    else:
        print "Cannot connect to database"

#I have to do this, since some 'bad' people who has name with non-ascii char
#UnicodeEncodeError: 'ascii' codec can't encode character u'\u0107' in position 13: ordinal not in range(128)
reload(sys) 
sys.setdefaultencoding('utf-8')
main()
