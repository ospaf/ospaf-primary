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

    def _githubGetMaxRemainAccount(self):
        max_remaining = 0
        i = 0
        for item in DMAccount.__account_queue__:
            if (item["core"]["remaining"] > DMAccount.__account_queue__[max_remaining]["core"]["remaining"]):
                max_remaining = i
            i += 1
        return max_remaining

    def githubGetFreeAccount(self):
        max_remaining = self._githubGetMaxRemainAccount()

        if DMAccount.__account_queue__[max_remaining]["core"]["remaining"] < 5:
            print "\n\n"
            print "Not healthy accout remained! Reload the status!"
            print "\n\n"
            self.init("github")
            max_remaining = self._githubGetMaxRemainAccount()
#TODO
            if DMAccount.__account_queue__[max_remaining]["core"]["remaining"] < 5:
                print "Fatal error in account!!!"
                exit(404)

        DMAccount.__account_queue__[max_remaining]["core"]["remaining"] -= 1
        return DMAccount.__account_queue__[max_remaining]

    def githubAccountRateLimit(self, col, item):
        login = item["login"]
        password = item["password"]
        auth_type = "Basic"
        if item.has_key("auth_type"):
            auth_type = item["auth_type"]
        if auth_type == "Basic":
            req = urllib2.Request("https://api.github.com/rate_limit")
            base64string = base64.encodestring('%s:%s' % (login, password)).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
        elif auth_type == "Oauth2":
            req = urllib2.Request("https://api.github.com/rate_limit?client_id=" + item["client_id"] + "&client_secret=" + item["client_secret"])
            #Oauth with Basic seems better!
            base64string = base64.encodestring('%s:%s' % (login, password)).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
        else:
            print "Unsupported user auth type " + auth_type
            return {"error": 1}

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

    def easyAddUser(self, col, item):
        auth_type = item["auth_type"]
        account_info = {"login": item["login"], "password": item["password"], "auth_type": auth_type, "type": col, "core": {"remaining": item["limit"]}}
        if auth_type == "Oauth2":
           account_info["client_id"] = item["client_id"]
           account_info["client_secret"] = item["client_secret"]
        
        DMAccount.__account_queue__.append(account_info)

    def addUser(self, col, item, add_to_db):
        if col == "github":
            res = self.githubAccountRateLimit(col, item)
            if res["error"] == 0:
                core_ele = res["val"]["resources"]["core"]
                print "Remaining " + str(core_ele["remaining"]) + " Limit " + str(core_ele["limit"])
                auth_type = "Basic"
                if item.has_key("auth_type"):
                    auth_type = item["auth_type"]
                account = {"auth_type": auth_type, "login": item["login"]}
                if auth_type == "Oauth2":
                    account["client_id"] = item["client_id"]
                    account["client_secret"] = item["client_secret"]
#login, type, client_id/client_secret should be uniq!
#An account could have lots of apps..               
                print account
                account_res = DMAccount.__account_db__[col].find_one(account)
#password, core info and reset_display might changes..
                account["password"] = item["password"]
                account["type"] = col
                account["core"] = core_ele
                account["core"]["reset_display"] = datetime.datetime.fromtimestamp(core_ele["reset"])
#TODO: check if account already in the queue!
                DMAccount.__account_queue__.append(account)

                if account_res:
                    DMAccount.__account_db__[col].update({"_id": account_res["_id"]}, {"$set": {"limit": core_ele["limit"], "password": item["password"]}})

                if add_to_db == False:
                    return
                else:
                    if account_res:
                        pass
                    else:
                        account_info = {"login": item["login"], "password": item["password"], "auth_type": auth_type, "limit": core_ele["limit"]}
                        if auth_type == "Oauth2":
                            account_info["client_id"] = item["client_id"]
                            account_info["client_secret"] = item["client_secret"]
                        account_res = DMAccount.__account_db__[col].insert(account_info)

    def loadFromFile(self, col, url):
        fo = open(url, "r")
        db_str = fo.read(100000)
        fo.close()
        val = json.loads(db_str)
        for item in val:
            self.addUser(col, item, True)

    def init(self, col):
        print "Init DMAccount"
        self.col = DMAccount.__account_db__[col]
        self.__account_queue__ = []
        res = self.col.find()
        easy_add = 0
        for item in res:
            print "Load " + item["login"] + "  auth type " + item["auth_type"]
            if easy_add:
                if item["auth_type"] == "Basic":
                    self.easyAddUser(col, item)
            else:
                self.addUser(col, item, False)

    def getRemaining(self):
        github_remaining = 0
        for item in DMAccount.__account_queue__:
            print item
            if item["type"] == "github":
                github_remaining += item["core"]["remaining"]
        return github_remaining

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

def test2():
    account = DMAccount()
    account.loadFromFile("github", "/home/novell/ospaf-primary/GithubUser/DMLib/tmp")

def test3():
    account = DMAccount()
#    account.loadFromFile("github", os.path.join(os.path.expanduser('~'), ".DMconf", "account_info"))
#    account.loadFromFile("github", os.path.join("/home/novell", ".DMconf", "account_info_001"))
#    account.addUser("github", {"auth_type": "Basic", "login": "suibian005", "password": "suibian0987654"}, True)
#    account.addUser("github", {"auth_type": "Oauth2", "login": "suibian002", "password": "qwe123456", "client_id": "baa50aa1bfd7df8fba9a", "client_secret": "e1746b9f3c99326297d7e079477bd380303fada2"}, True)
    account.addUser("github", {"auth_type": "Basic", "login": "dq001", "password": "qwe123456"}, True)
    account.addUser("github", {"auth_type": "Basic", "login": "dq002", "password": "qwe123456"}, True)
#    account.getInfo()

def test4():
    account = DMAccount()
    account.init("github")
    account.getInfo()

#test2()
#test3()
test4()
