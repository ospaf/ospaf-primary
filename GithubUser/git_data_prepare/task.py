import sys
sys.path.append("../..")
sys.path.append("../../..")
sys.path.append("..")
import re
import threading
import socket
import base64
import json
import httplib
import urllib
import urllib2
import datetime
import pymongo
from pymongo import MongoClient
from GithubUser.DMLib.DMDatabase import DMDatabase
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers
from GithubUser.DMLib.DMTask import DMTask

from event.event import GithubEvent

def test():
    task1 = DMTask()
    val = {"name": "fake-event", "action_type": "loop", "start": 6000000, "end": 6001000}

    task1.init_test("github", val)
    e1 = GithubEvent(task1)
    e1.runTask()
    task1.remove()

test()


