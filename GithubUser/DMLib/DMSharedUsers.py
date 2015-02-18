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

    def readURL(self, url, params):
        fu = DMSharedUsers().__shared_account__.githubGetFreeAccount()
        return self._readURL(url, fu, params)

    def _readURL(self, url, user, params):
        auth_type = "Basic"
        if user.has_key("auth_type"):
            auth_type = user["auth_type"]
        if auth_type == "Basic":
            data=urllib.urlencode(params)
            if data and len(data) > 1:
#FIXME: better lib call?
                req = urllib2.Request(url+"?"+data)
            else:
                req = urllib2.Request(url)
            base64string = base64.encodestring('%s:%s' % (user["login"], user["password"])).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
        elif auth_type == "Oauth2":
            params["client_id"] = user["client_id"]
            params["client_secret"] = user["client_secret"]
            data=urllib.urlencode(params)
            req = urllib2.Request(url+"?"+data)
            base64string = base64.encodestring('%s:%s' % (user["login"], user["password"])).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
        else:
            print "fatal user error!"
            return {"error": 1}

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


def test_oauth():
#    url = "https://api.github.com/repos/SeoHyeonDeok/flask/contributors?page=1&client_id=baa50aa1bfd7df8fba9a&client_secret=e1746b9f3c99326297d7e079477bd380303fada2"
    url = "https://api.github.com/repos/SeoHyeonDeok/flask/contributors"
    new_url = "https://api.github.com/repos/SeoHyeonDeok/flask/contributors?client_id=baa50aa1bfd7df8fba9a&client_secret=e1746b9f3c99326297d7e079477bd380303fada2"
    client_id = "baa50aa1bfd7df8fba9a"
    client_secret = "e1746b9f3c99326297d7e079477bd380303fada2"
    params = {}
    params["client_id"] = client_id
    params["client_secret"] = client_secret
    data = urllib.urlencode(params)
    print data
    if data:
        req = urllib2.Request(url+"?"+data)
#, data=data)
#    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req, timeout=300)
    res = res_data.read()
    print res

#test_oauth()
