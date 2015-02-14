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
from user_repo.repo import GithubRepo
from follower.followers import GithubFollowers
from repositories.repositories import GithubRepositories
from contributors.contributors import GithubContributors

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
        r1.generateToFile(file)

def import_event(start, end):
    gap = 1000
    for i in range (start, end):
        task = DMTask()
        val = {"name": "get_events", "action_type": "loop", "start": i * gap, "end": (i+1)*gap}
        task.init("github", val)
        r1 = GithubEvent(task)
        file = "./TaskFinishedFiles/get_events_start_" + str(i*gap)+".output"
        r1.runTaskFromFile(file)

def main_unit():
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

user_thread = []
gap = 1000

class myThread (threading.Thread):
    def __init__(self, cmd, start, end, endless):
        threading.Thread.__init__(self)
        self.endless = endless
        self.set(cmd, start, end)

    def set(self, cmd, start, end):
        self.task = DMTask()
        self.r = None
        self.val = {"action_type": "loop", "start": start, "end": end}
        if cmd == "get_repos":
            self.val["name"] = "get_repos"
            self.task.init("github", self.val)
            self.r = GithubRepo(self.task)
        elif cmd == "get_followers":
            self.val["name"] = "get_followers"
            self.task.init("github", self.val)
            self.r = GithubFollowers(self.task)
        elif cmd == "get_events":
            self.val["name"] = "get_events"
            self.task.init("github", self.val)
            self.r = GithubEvent(self.task)
# TODO: do not support now
#        elif cmd == "get_users":
#            self.val["name"] = "get_users"
#            self.task.init("github", self.val)
#            self.r = GithubUser(self.task)
        elif cmd == "get_repositories":
            self.val["name"] = "get_repositories"
            self.task.init("github", self.val)
            self.r = GithubRepositories(self.task)
        elif cmd == "get_contributors":
            self.val["name"] = "get_contributors"
            self.task.init("github", self.val)
            self.r = GithubContributors(self.task)
        else:
            print "Failed to init the task"
            return 0
        return 1

    def run(self):
        print "Starting " + str(self.val)
        if self.r:
            self.r.runTask()
        print "Exiting " + str(self.val)

        if self.endless == 1:
            while 1:
                query = {"col": "github", "num": 1, "query": {"status": "init"}}
                res = DMTask().getFreeTasks(query)
                if res:
                    for item in res:
                        print item
                        if self.set(item["name"], item["start"], item["end"]) == 1:
                            self.r.runTask()
                        else:
                            return
                        print "\n Start another task in the finished thread\n"
                        break

def run_task():
    for item in user_thread:
        item.start()

def main_loop():
    cmd = sys.argv[1]
    start = long(sys.argv[2])
    end = long(sys.argv[3])

    if cmd == "gen_event":
        gen_event (start, end)   
        return
    elif cmd == "import_event":
        import_event (start, end)
        return

    for i in range (start, end):
        new_thread = myThread(cmd, i, i+1)
        user_thread.append(new_thread)

    run_task()

def run_free_task(num, endless):
    query = {"col": "github", "num": num, "query": {"status": "init"}}
#    query = {"col": "obs", "num": num, "query": {"status": "init"}}
    res = DMTask().getFreeTasks(query)
    i = 0
    for item in res:
        new_thread = myThread(item["name"], item["start"], item["end"], endless)
        user_thread.append(new_thread)
        i += 1
    print str(i) + " task received, start to run them!"
    run_task()

#main_loop()
def main_free_task():
    timeout = 300
    socket.setdefaulttimeout(timeout)
    if len(sys.argv) < 2:
        print "Please input the task you need to get"
        return

    num = long(sys.argv[1])
    endless = 1
    run_free_task(num, endless)

main_free_task()
