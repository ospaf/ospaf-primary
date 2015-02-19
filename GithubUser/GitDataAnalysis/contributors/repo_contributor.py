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
          
def repo_user(db, login, count):
    user = db["user"].find_one({"login": login})
    if user is None:
#FIXME: should reload it!
        print "User " + login + " is not exist"
        return
    email = " "
    name = " "
    company = " "
    location = " "
    if user.has_key("email") and user["email"] is not None:
        email = " Email " + user["email"]
    if user.has_key("name") and user["name"] is not None:
        name = " Name " + user["name"]
    if user.has_key("company") and user["company"] is not None:
        company = " Company " + user["company"]
    if user.has_key("location") and user["location"] is not None:
        location = " Location " + user["location"]
    print "User " + login + email + name + company + location + "  Count " + str(count)

def report_repo(db, repo_name):
    repo_res = db["repositories"].find_one({"full_name": repo_name})
    if repo_res:
        print repo_res["contributors_count"]
        whole_count = 0
        contributor_res = db["contributors"].find_one({"id": repo_res["id"]})
        for item in contributor_res["contributors"]:
            count = item["contributions"]
            login = item["login"]
            repo_user(db, login, count)
            whole_count += count
        print "Whole count " + str(whole_count)
    else:
        return

def main ():
    dm_db = DMDatabase()
    db = dm_db.getDB()
    if (db):
        repo_name = "openstack/horizon"
        report_repo(db, repo_name)
    else:
        print "Cannot connect to database"

#I have to do this, since some 'bad' people who has name with non-ascii char
#UnicodeEncodeError: 'ascii' codec can't encode character u'\u0107' in position 13: ordinal not in range(128)
reload(sys) 
sys.setdefaultencoding('utf-8')
main()
