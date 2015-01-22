import sys
sys.path.append("../../..")
import re
import threading
import socket
import base64
import httplib
import urllib
import urllib2
import datetime
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers

class GithubEventNoDB:
    def __init__(self, input_file):
        self.input_file = input_file
        self.fo = open(input_file, "r")
        url = input_file + '.output'
        self.fw = open(url, "w")
        self.status = 1

    def append_event(self, gh_user_id, page):
        url = "https://api.github.com/users/"+gh_user_id+"/events?page="+str(page);
        print url
        return DMSharedUsers().readURL(url)

    def upload_user_event(self, user_login):
        need_update = 0
        print user_login
        new_res = self.user_event_list(user_login)
        if (new_res["error"] == 1):
#TODO we should save this error in order to do it again!
            return 1

        count = len(new_res["val"])

        if count > 0:
            print user_login + " added with " + str(count) + " counts"
# KEY!
#        self.db["event"].insert({"login": user_login, "event": new_res["val"], "count": count, "update_date": datetime.datetime.utcnow()})
        if self.status == 1:
            self.status = 0
        else:
            self.fw.write(",\n")
        data_json = {"login": user_login, "event": new_res["val"], "count": count, "update_date": datetime.datetime.utcnow()}
        self.fw.write(str(data_json))
        return 0

    def user_event_list(self, user_login):
        res = []
        i = 1
        while 1:
            ret_val = self.append_event(user_login, i)
            if ret_val["error"] == 1:
                if i > 2:
#   "message": "In order to keep the API fast for everyone, pagination is limited for this resource. Check the rel=last link relation in the Link response header to see how far back you can traverse.",
#  "documentation_url": "https://developer.github.com/v3/#pagination"
                    return {"error": 0, "val": res}
                else:
                    return {"error": 1}
            if len(ret_val["val"]) > 0:
                res += ret_val["val"]
                if len(ret_val["val"]) < 30:
                    break
            else:
                break

            i += 1
# simply return if event > 10..
            if i > 10:
                break

        return {"error": 0, "val": res}

#we give logins to each task
    def runTask(self):
        self.fw.write("[")
        for line in self.fo.readlines():
            line = line.strip()
            if not len(line):
                continue
            elif line.startswith('#'):
                continue
            else:
                ret = self.upload_user_event(line)
                if ret == 1:
#TODO make a better error message
                    continue

        self.fw.write("]")
        print "Task finish, exiting the thread"

#test()


