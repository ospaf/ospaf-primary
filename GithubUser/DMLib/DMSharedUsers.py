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
    def __init__(self):
        if len(DMSharedUsers.__shared_users__) > 0:
            return
        fo = open(os.path.join(os.path.expanduser('~'), ".DMconf", "account_info"), "r")
        db_str = fo.read(100000)
        fo.close()
        val = json.loads(db_str)
        for item in val:
            item["count"] = 0
            DMSharedUsers.__shared_users__.append(item)

    def getFreeUser(self):
# TODO, sync with github ..
        min_count = 0
        i = 0
        for item in DMSharedUsers.__shared_users__:
            if (item["count"] < DMSharedUsers.__shared_users__[min_count]["count"]):
                min_count = i
            i += 1
        DMSharedUsers.__shared_users__[min_count]["count"] += 1
        return DMSharedUsers.__shared_users__[min_count]

# add and update the password
    def addFreeUser(self, login, password):
# TODO, save to file?
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
        base64string = base64.encodestring('%s:%s' % (fu["login"], fu["password"])).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)

        try:
            res_data = urllib2.urlopen(req)
        except urllib2.URLError, err:
# TODO we should note this ...
            print 'dliang url error' + url + "  user  " + fu["login"]
            print err
            return {"error": 1}
        except urllib2.HTTPError, err:
            print '404 error'
            if err.code == 404:
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

