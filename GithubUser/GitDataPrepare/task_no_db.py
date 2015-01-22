import sys
sys.path.append("../..")
sys.path.append("../../..")
sys.path.append("..")
import re
import threading
import socket
import base64
import httplib
import urllib
import urllib2
import datetime
from GithubUser.DMLib.DMSharedUsers import DMSharedUsers

from event.event_no_db import GithubEventNoDB

def test1():
    task = {"name": "fake-event", "action_type": "loop", "start": 10000, "end": 10001, "logins": ["initlove"]}

    e1 = GithubEventNoDB(task)
    e1.runTask()

def test():
    test1()

def event(task_file):
    r1 = GithubEventNoDB(task_file)
    r1.runTask()



class myThread (threading.Thread):
    def __init__(self, task_file):
        threading.Thread.__init__(self)
        self.task_file = task_file
        self.task = GithubEventNoDB(task_file)

    def run(self):
        print "Starting " + str(self.task_file)
        self.task.runTask()
        print "Exiting " + str(self.task_file)

def run_task():
    for item in user_thread:
        item.start()

user_thread = []

def main():
    dir = "/tmp/task_input/"
    for i in range (1003, 1023):
        url = "/tmp/task_input/get_events_start_" + str(i*1000)
        new_thread = myThread(url)
        user_thread.append(new_thread)

    run_task()

main()
