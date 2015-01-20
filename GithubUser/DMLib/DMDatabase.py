import os
import sys
import base64
import json
import pymongo
from pymongo import MongoClient

#TODO try catch...
class DMDatabase:
    __dm_database__ = None
    def __init__(self):
        if DMDatabase.__dm_database__ is not None:
            return
        fo = open(os.path.join(os.path.expanduser('~'), ".DMconf", "database_info"), "r")
        db_str = fo.read(10000)
        fo.close()
        val = json.loads(db_str)

        client = MongoClient(val["addr"], val["port"])
        DMDatabase.__dm_database__ = client[val["db_name"]]

    def getDB(self):
        return DMDatabase.__dm_database__

    def DBStatus(self):
        print "DB Status:"

