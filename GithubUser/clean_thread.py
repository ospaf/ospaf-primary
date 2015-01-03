#!/usr/bin/python

import threading
import time
import base64
import os
import sys

dir_conf = [
    {"dir": "./get_user_data_0_to_50/", "conf" : "0_to_50", "new": "0_to_50.new"},
    {"dir": "./get_user_data_50_to_100/", "conf" : "50_to_100", "new": "50_to_100.new"},
    {"dir": "./get_user_data_100_to_150/", "conf" : "100_to_150", "new": "100_to_150.new"},
    {"dir": "./get_user_data_150_to_200/", "conf" : "150_to_200", "new": "150_to_200.new"},
    {"dir": "./get_user_data_200_to_250/", "conf" : "200_to_250", "new": "200_to_250"},
    {"dir": "./get_user_data_250_to_300/", "conf" : "250_to_300", "new": "250_to_300"},
    {"dir": "./get_user_data_350_to_400/", "conf" : "350_to_400", "new": "350_to_400"}
]

user_task = [
]

user_thread = [
]

def send_dir_request(dir, config_file):
    conf_file = dir+config_file
    fo = open(conf_file, "r")
    for line in fo.readlines():
        line = line.strip()
        if not len(line):
            continue
        elif line.startswith('#'):
            print line
        else:
            uri = dir + `line` + ".txt"
            if os.path.isfile(uri):
                print '#'+line
            else:
                print line
            continue


id = long(sys.argv[1])
send_dir_request(dir_conf[id]["dir"], dir_conf[id]["conf"])
