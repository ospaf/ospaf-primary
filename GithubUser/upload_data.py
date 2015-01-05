import base64
import json

from os import walk

import pymongo
from pymongo import MongoClient

_db_addr = "147.2.207.55"
_db_port = 27017
_db_name = "github"
_db_collection = "user"

client = MongoClient(_db_addr, _db_port)
dc = client[_db_name][_db_collection]
count = 0


for (dirpath, dirnames, filenames) in walk("./"):
    for file_txt in filenames:
        if (file_txt.find("txt") > 3):
            fo = open(file_txt, "r")
            str = fo.read(1000000)
            fo.close()
            val = json.loads(str)
# if we create index on 'id' and make it uniq, we can make it much more fast!
# no need to find, just insert it
            new1 = dc.find_one({'id': val["id"]})
            if new1:
                print "we already got it!"
            else:
#                print "we can insert it!"
                count += 1
                if count%100 == 0:
                    print count
                dc.insert(val)
