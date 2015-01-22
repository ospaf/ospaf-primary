#!/usr/bin/python

import threading
import time
import base64
import os
import sys

dir_conf = [
    {"dir": "./get_user_data_0_to_50/", "conf" : "0_to_50", "new": "0_to_50"},
    {"dir": "./get_user_data_50_to_100/", "conf" : "50_to_100", "new": "50_to_100"},
    {"dir": "./get_user_data_100_to_150/", "conf" : "100_to_150", "new": "100_to_150"},
    {"dir": "./get_user_data_150_to_200/", "conf" : "150_to_200", "new": "150_to_200"},
    {"dir": "./get_user_data_200_to_250/", "conf" : "200_to_250", "new": "200_to_250"},
    {"dir": "./get_user_data_250_to_300/", "conf" : "250_to_300", "new": "250_to_300"},
    {"dir": "./get_user_data_300_to_350/", "conf" : "300_to_350", "new": "300_to_350"},
    {"dir": "./get_user_data_350_to_400/", "conf" : "350_to_400", "new": "350_to_400"}
]

user_task = [
]

user_thread = [
]

def send_dir_request(dir, config_file, new_file):
    conf_file = dir+config_file
    print conf_file
    fo = open(conf_file, "r")
    fw = open(new_file, "w")
    for line in fo.readlines():
        line = line.strip()
        if not len(line):
            continue
        elif line.startswith('#'):
            continue
        else:
            uri = dir + `line` + ".txt"
            if os.path.isfile(uri):
                continue
            else:
                fw.write(line)
                fw.write('\n')
#                print line
            continue


for item in dir_conf:
    send_dir_request(item["dir"], item["conf"], item["new"])
