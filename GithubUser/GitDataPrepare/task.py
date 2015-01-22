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
from repo.repo import GithubRepo
from follower.followers import GithubFollowers

def test1():
    task = DMTask()
    val = {"name": "fake-event", "action_type": "loop", "start": 10000, "end": 10001}

    task.init_test("github", val)
    e1 = GithubEvent(task)
    e1.runTask()
    task.remove()

def test2():
    task = DMTask()
    val = {"name": "fake-repo", "action_type": "loop", "start": 10000, "end": 10001}

    task.init_test("github", val)
    e1 = GithubRepo(task)
    e1.runTask()
    task.remove()

def test3():
    task = DMTask()
    val = {"name": "fake-followers", "action_type": "loop", "start": 10000, "end": 10001}

    task.init_test("github", val)
    e1 = GithubFollowers(task)
    e1.runTask()
    task.remove()

def test():
    test1()
    test2()
    test3()

test()
