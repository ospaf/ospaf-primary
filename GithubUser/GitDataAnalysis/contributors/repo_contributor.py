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
     
def report_small_by_repo_user(client, user):
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
    print "User " + user["login"] + email + name + company + location + "  Count " + str(user["contributions"])

def report_small_by_repo(client, user_name, repo_name):
    repo_res = client[user_name][repo_name].find()
    total_contributors = 0
    whole_count = 0
    for item in repo_res:
        report_small_by_repo_user(client, item)
        whole_count += item["contributions"]
        total_contributors += 1
    print "Whole commits " + str(whole_count) + "  in " + str(total_contributors) + " people"

def generate_small_by_repo_user(client, user_name, repo_name, contributor_login, count):
    user = client["github"]["user"].find_one({"login": contributor_login})
    if user is None:
#FIXME: should reload it!
        print "User " + contributor_login + " is downloaded, now reload it!"
        addOneUser(client["github"], contributor_login)
        user = client["github"]["user"].find_one({"login": contributor_login})
        if user is None:
            print "User " + contributor_login + " is not exist in github anymore!"
            return
    
    saved_res = client[user_name][repo_name].find_one({"id": user["id"]})
    if saved_res:
        pass
    else:
        user["contributions"] = count
        client[user_name][repo_name].insert(user)

def generate_small_by_repo(client, user_name, repo_name):
#FIXME: should use contributors find directly, but for now, we don't have index on contributors.full_name...
    repo_res = client["github"]["repositories"].find_one({"full_name": user_name+'/'+repo_name})
    if repo_res:
        contributor_res = client["github"]["contributors"].find_one({"id": repo_res["id"]})
        for item in contributor_res["contributors"]:
            count = item["contributions"]
            contributor_login = item["login"]
            generate_small_by_repo_user(client, user_name, repo_name, contributor_login, count)

        saved_res = client[user_name]["repositories"].find_one({"id": repo_res["id"]})
        if saved_res:
            pass
        else:
            client[user_name]["repositories"].insert(repo_res)
    else:
        return

def main ():
    dm_db = DMDatabase()
    client = dm_db.getClient()
    if (client):
#user name is a database
#repo_name is col to store repos that
#user is another col to store contributors' info
        user_name = "openstack"
        full_name = "openstack/horizon"
        repo_name = "horizon"
#        generate_small_by_repo(client, user_name, repo_name)
        report_small_by_repo(client, user_name, repo_name)
    else:
        print "Cannot connect to database"

#I have to do this, since some 'bad' people who has name with non-ascii char
#UnicodeEncodeError: 'ascii' codec can't encode character u'\u0107' in position 13: ordinal not in range(128)
reload(sys) 
sys.setdefaultencoding('utf-8')
main()
