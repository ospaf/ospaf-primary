import sys
import os
import base64
import json
import urllib
import urllib2

import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from DMDatabase import DMDatabase

class DMAccount:
    __account_client__ = None
    __account_db__ = None
    __account_queue__ = []
    def __init__(self):
        if DMAccount.__account_db__ is not None:
            return
        DMAccount.__account_client__ = DMDatabase().getClient()
        DMAccount.__account_db__ = DMAccount.__account_client__["account"]

    def githubUserRateLimit(self, col, item):
        login = item["login"]
        password = item["password"]
        req = urllib2.Request("https://api.github.com/rate_limit")
        base64string = base64.encodestring('%s:%s' % (login, password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        try:
            res_data = urllib2.urlopen(req)
        except urllib2.HTTPError, err:
            print err.read()
            if err.code == 404:
                 return {"error": 1}
        except urllib2.URLError, err:
# TODO we should note this ...
            if hasattr(err, 'reason'):
                print err.reason
            elif hasattr(err, 'code'):
                print err.code
            print 'dliang url error' + "  user  " + login
            print err.read()
            return {"error": 1, "error_code": 110}
        except httplib.HTTPException, err:
            print 'http exception'
            return {"error": 1}
# TODO timeout
        else:
            res = res_data.read()
            if res:
                val = json.loads(res)
                return {"error": 0, "val": val}
            return {"error": 1}
        return {"error": 1}

    def addUser(self, col, item, add_to_db):
        if col == "github":
            res = self.githubUserRateLimit(col, item)
            if res["error"] == 0:
                core_ele = res["val"]["resources"]["core"]
                account = {"login": item["login"], "password": item["password"], "type": col, "core": core_ele}
                account["core"]["reset_display"] = datetime.datetime.fromtimestamp(core_ele["reset"])
#TODO: check if account already in the queue!
                DMAccount.__account_queue__.append(account)
                if add_to_db == False:
                    return
                else:
                    account_res = DMAccount.__account_db__[col].find_one({"login": item["login"]})
                    if account_res:
                        pass
                    else:
                        account_res = DMAccount.__account_db__[col].insert({"login": item["login"], "password": item["password"]})


    def loadFromFile(self, col, url):
        fo = open(url, "r")
        db_str = fo.read(100000)
        fo.close()
        val = json.loads(db_str)
        for item in val:
            self.addUser(col, item, True)

    def init(self, col):
        self.col = DMAccount.__account_db__[col]
        res = self.col.find()
        for item in res:
            print "Load " + item["login"]
            self.addUser(col, item, False)

    def getInfo(self):
        github_remaining = 0
        github_accounts = 0
        for item in DMAccount.__account_queue__:
            if item["type"] == "github":
                github_accounts += 1
                github_remaining += item["core"]["remaining"]
            print item
        if github_accounts > 0:
            print str(github_accounts) + "github accounts  " + str(github_remaining) + " remaining API calls. "

# prefer not to use this ..
    def removeUser (self, col, item):
         pass

def test3():
    account = DMAccount()
#    account.loadFromFile("github", os.path.join(os.path.expanduser('~'), ".DMconf", "account_info"))
#    account.loadFromFile("github", os.path.join("/home/novell", ".DMconf", "account_info_001"))
    account.addUser("github", {"login": "githubDM001", "password": "qwe123456"}, True)
    account.getInfo()

def test4():
    account = DMAccount()
    account.init("github")
    account.getInfo()

test3()
