import sys
import os
import base64
import json

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

