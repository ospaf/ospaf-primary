import sys
import os
import base64
import json
import json
import httplib
import urllib
import urllib2
import datetime
from DMAccount import DMAccount

class DMSharedUsers:
    __shared_account__ = None

    def __init__(self):
        if DMSharedUsers.__shared_account__ is not None:
            return
        print "__init DMSharedUsers"
        DMSharedUsers.__shared_account__ = DMAccount()
        DMSharedUsers.__shared_account__.init("github")

#TODO: shareduser and Account show do that individually
    def getRemaining(self):
        return DMSharedUsers.__shared_account__.getRemaining()

    def readURL(self, url):
        req = urllib2.Request(url)
        fu = DMSharedUsers().__shared_account__.githubGetFreeAccount()
        return self._readURL(url, fu)

    def _readURL(self, url, user):
        req = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (user["login"], user["password"])).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)

        try:
#TODO: 300?
            res_data = urllib2.urlopen(req, timeout=300)
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

