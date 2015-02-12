import sys
import os
import base64
import json
import json
import httplib
import urllib
import urllib2
import datetime

#TODO try catch...

class DMSharedUsers:
    __shared_users__ = []
    def _load_users(self):
        DMSharedUsers.__shared_users__ = []
        fo = open(os.path.join(os.path.expanduser('~'), ".DMconf", "account_info"), "r")
        db_str = fo.read(100000)
        fo.close()
        val = json.loads(db_str)
        for item in val:
            res = self.limitRemains(item)
            if res["status"] == "OK":
                item["remaining"] = res["core"]["remaining"]
                item["reset"] = res["core"]["reset"]
                DMSharedUsers.__shared_users__.append(item)

    def __init__(self):
        if len(DMSharedUsers.__shared_users__) > 0:
            return
        self._load_users()

#https://developer.github.com/v3/rate_limit/
    def limitRemains(self, user):
        url = "https://api.github.com/rate_limit"
        res = self._readURL(url, user)
        if res["error"] == 1:
            return {"status": "Failed"}
        else:
            return {"status": "OK", "core": res["val"]["resources"]["core"]}

    def _getMaxUser(self):
        max_remaining = 0
        i = 0
        for item in DMSharedUsers.__shared_users__:
            if (item["remaining"] > DMSharedUsers.__shared_users__[max_remaining]["remaining"]):
                max_remaining = i
            i += 1
        return max_remaining

    def getFreeUser(self):
        max_remaining = self._getMaxUser()

# This is just a current solution, we need a single demo to keep track of the account
#   since we may have multiply process
        if DMSharedUsers.__shared_users__[max_remaining]["remaining"] < 10:
            print "\n\n"
            print "Not healthy accout remained! Reload the status!"
            print "\n\n"
            self._load_users()
            max_remaining = self._getMaxUser()
#TODO
            if DMSharedUsers.__shared_users__[max_remaining]["remaining"] < 10:
                print "Fatal error!!!"

        DMSharedUsers.__shared_users__[max_remaining]["remaining"] -= 1
        return DMSharedUsers.__shared_users__[max_remaining]

# add and update the password
    def addFreeUser(self, login, password):
        for item in DMSharedUsers.__shared_users__:
            if item["login"] == login:
                if item["password"] == password:
                    return
                else:
                    item["password"] = password
                    return
        DMSharedUsers.__shared_users__.append({"login": login, "password": password})

#TODO connect with server will be better
    def accountStatus(self):
        print "AccountInfo: "
        print DMSharedUsers.__shared_users__

    def readURL(self, url):
        req = urllib2.Request(url)
        fu = DMSharedUsers().getFreeUser()
        return self._readURL(url, fu)

    def _readURL(self, url, user):
        req = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (user["login"], user["password"])).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)

#TODO: where meeting this, I think I should give it 3 times!
#<urlopen error [Errno 110] Connection timed out>
        try:
            res_data = urllib2.urlopen(req)
        except urllib2.HTTPError, err:
            if hasattr(err, "code"):
                return {"error": 1, "error_code": err.code}
            else:
# WRONG!
                return {"error": 1}
        except urllib2.URLError, err:
            if hasattr(err, "code"):
                return {"error": 1, "error_code": err.code}
            else:
                return {"error": 1}
        except httplib.HTTPException, err:
            print 'http exception'
            return {"error": 1}
# TODO timeout
        else:
            res = res_data.read()
            if res:
                val = json.loads(res)
                return {"error": 0, "val": val}
            else:
#TODO: FIXME: why such following url has no contributors page?
#https://api.github.com/repos/pganuysh/test/contributors?page=1
                return {"error": 1}

        print "How to get here?"
        return {"error": 1}

