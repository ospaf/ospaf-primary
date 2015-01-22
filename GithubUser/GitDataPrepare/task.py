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

def repo(start, end):
    gap = 1000
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_repos", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r1 = GithubRepo(task)
        r1.runTask()


def followers(start, end):
    gap = 1000
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_followers", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r1 = GithubFollowers(task)
        r1.runTask()

def event(start, end):
    gap = 1000
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_events", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r1 = GithubEvent(task)
        r1.runTask()

def gen_event(start, end):
    gap = 1000
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_events", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r1 = GithubEvent(task)
        file = "./TaskFiles/get_events_start_" + str(i*gap)
        r1.generate(file)

def main():
    cmd = sys.argv[1]
    start = long(sys.argv[2])
    end = long(sys.argv[3])

    print cmd + ' ' +str(start) + ' ' + str(end)

    if cmd == "repo":
        repo(start, end)
    elif cmd == "followers":
        followers(start, end)
    elif cmd == "event":
        event(start, end)
    elif cmd == "gen-event":
        gen_event(start, end)

main()
