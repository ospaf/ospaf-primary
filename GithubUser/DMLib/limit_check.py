import sys
import base64
import json
import urllib
import urllib2
import datetime
import os

def limitStatus(item):
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

def main():
    fo = open(os.path.join(os.path.expanduser('~'), ".DMconf", "account_info"), "r")
    db_str = fo.read(100000)
    fo.close()
    val = json.loads(db_str)
    for item in val:
        res = limitStatus(item)
        if res["error"] == 0:
           core_ele = res["val"]["resources"]["core"]
           print item["login"] + "\t" + str(core_ele["limit"]) + "\t" +  str(core_ele["remaining"]) + "\t" + str(datetime.datetime.fromtimestamp(core_ele["reset"]))

main()
