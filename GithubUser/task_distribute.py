#!/usr/bin/python

import threading
import time
import base64
import os
import sys
import urllib
import urllib2

user_pass = [
    {"user":"githublover001", "password": "qwe123456", "count": 0},
    {"user":"githublover002", "password": "qwe123456", "count": 0},
    {"user":"githublover003", "password": "qwe123456", "count": 0},
    {"user":"githublover004", "password": "qwe123456", "count": 0},
    {"user":"githublover005", "password": "qwe123456", "count": 0},
    {"user":"githublover006", "password": "qwe123456", "count": 0},
    {"user":"githublover007", "password": "qwe123456", "count": 0},
    {"user":"githublover008", "password": "qwe123456", "count": 0},
    {"user":"githublover009", "password": "qwe123456", "count": 0},
    {"user":"githublover010", "password": "qwe123456", "count": 0},
    {"user":"githublover011", "password": "qwe123456", "count": 0},
    {"user":"githublover012", "password": "qwe123456", "count": 0},
    {"user":"githublover013", "password": "qwe123456", "count": 0},
    {"user":"githublover014", "password": "qwe123456", "count": 0},
    {"user":"githublover015", "password": "qwe123456", "count": 0},
    {"user":"githublover016", "password": "qwe123456", "count": 0},
    {"user":"githublover017", "password": "qwe123456", "count": 0},
    {"user":"githublover018", "password": "qwe123456", "count": 0},
    {"user":"githublover019", "password": "qwe123456", "count": 0},
    {"user":"githublover020", "password": "qwe123456", "count": 0},
    {"user":"githublover021", "password": "qwe123456", "count": 0},
    {"user":"githublover022", "password": "qwe123456", "count": 0},
    {"user":"githublover023", "password": "qwe123456", "count": 0},
    {"user":"githublover024", "password": "qwe123456", "count": 0},
    {"user":"githublover025", "password": "qwe123456", "count": 0},
    {"user":"githublover026", "password": "qwe123456", "count": 0},
    {"user":"githublover027", "password": "qwe123456", "count": 0},
    {"user":"githublover028", "password": "qwe123456", "count": 0},
    {"user":"githublover029", "password": "qwe123456", "count": 0},
    {"user":"githublover030", "password": "qwe123456", "count": 0},
    {"user":"githublover031", "password": "qwe123456", "count": 0},
    {"user":"githublover032", "password": "qwe123456", "count": 0}
]

# this is the example!
dir_conf = [
    {"dir": "./get_user_data_0_to_50/", "conf" : "0_to_50", "total": 500000},
    {"dir": "./get_user_data_50_to_100/", "conf" : "50_to_100", "total": 500000},
    {"dir": "./get_user_data_100_to_150/", "conf" : "100_to_150", "total": 500000}
]

user_task = [
]

user_thread = [
]

def get_free_user():
    min_count = 0
    i = 0
    for item in user_pass:
        if (item["count"] < user_pass[min_count]["count"]):
            min_count = i
        i += 1
    user_pass[min_count]["count"] += 1
    return min_count

def send_request(user_loop, dir, gh_user_login):
        url = "https://api.github.com/users/"+gh_user_login
        uri = dir + `gh_user_login` + ".txt"
#        print uri
        print url 
        if os.path.isfile(uri):
            print 'exist'
            return -1
        req = urllib2.Request(url)
        username = user_pass[user_loop]["user"]
        password = user_pass[user_loop]["password"]
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        user_pass[user_loop]["count"] += 1

        try:
            res_data = urllib2.urlopen(req)
        except urllib2.HTTPError, err:
            if err.code == 404:
                 return -404
        else:
            res = res_data.read()
            text_file = open(uri, "w")
            text_file.write(res)
            text_file.close()
            return 0

        return 0

# each thread call 'send_dir_request'
def send_dir_request(task):
    user_loop = task["user_loop"]
    dir = task["dir"]
    config_file = task["conf"]
    begin = task["begin"]
    end = task["end"]
    conf_file = dir+config_file
    i = 0
    fo = open(conf_file, "r")
    for line in fo.readlines():
        i += 1
        if (i < begin):
            continue
        elif (i > end):
            break
        line = line.strip()
        if not len(line) or line.startswith('#'):
            continue
        else:
            ret_val = send_request(user_loop, dir, line)
            if (ret_val == -1):
                continue
            if (ret_val == -404):
                continue


def init_task():
#each dir, we start 5 tasks now!
    num = 5
    for item in dir_conf:
        gap = item["total"]/5
        for i in range(0, num):
            begin = i * gap
            if (i == (num -1)):
                end = item["total"]
            else:
                end = (i+1) * gap
            new_task = {}
            new_task["dir"]=item["dir"]
            new_task["conf"]=item["conf"]
            new_task["user_loop"]=get_free_user()
            new_task["begin"] = begin
            new_task["end"] = end
            user_task.append(new_task)
       
def debug_task():
    print "Total len "
    print len(user_task)
    print user_task

def distribute_task():
    i = 0
    for item in user_task:
        name = "Thread " + str(i)
        new_thread = myThread(item, name)
        user_thread.append(new_thread)
        i += 1


class myThread (threading.Thread): 
    def __init__(self, task, name):
        threading.Thread.__init__(self)
        self.task = task
        self.name = name
    def run(self):        
#        print "Starting " + self.name
        send_dir_request(self.task)
#        print "Exiting " + self.name

def run_task():
    for item in user_thread:
        item.start()

exitFlag = 0

init_task()
#debug_task()
distribute_task()
run_task()

#print "Exiting Main Thread"
