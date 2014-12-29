# This is used after generate_logins.py 
# read the config file filled with "login" 

import base64
import os
import sys
import urllib
import urllib2

user_pass = [
    {"user":"githublover011", "password": "qwe123456", "count": 0},
    {"user":"githublover012", "password": "qwe123456", "count": 0},
    {"user":"githublover013", "password": "qwe123456", "count": 0},
    {"user":"githublover014", "password": "qwe123456", "count": 0}
]

def send_request(gh_user_id, i):
        url = "https://api.github.com/users/"+gh_user_id;
        print url
        if os.path.isfile(`gh_user_id`+".txt"):
            print 'exist'
            return -1
        req = urllib2.Request(url)
        username = user_pass[i]["user"]
        password = user_pass[i]["password"]
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)   
        user_pass[i]["count"] += 1
        try:
            res_data = urllib2.urlopen(req)
# In some cases, the 'login' is not exist any more, we can just skip it!
        except urllib2.HTTPError, err:
            if err.code == 404:
                 return -404
        else:
            res = res_data.read()
            text_file = open(`gh_user_id`+".txt", "w")
            text_file.write(res)
            text_file.close()
            return 0

        return 0


def main():
    conf_len = len(sys.argv)
    if (conf_len >= 2):
        conf_file = sys.argv[1]
    else:
        conf_file = "config"

    if (conf_len >= 4):
        begin = sys.argv[2]
        end = sys.argv[3]
    else:
        begin = 0
        end = 10000000
    i = 0

    fo = open(conf_file, "r")
    for line in fo.readlines():
        i++
        if (i > end):
            break
        elif (i < begin):
            continue
    
        line = line.strip()                             
        if not len(line) or line.startswith('#'):       
            continue            
        else:
            ret_val = send_request(line, 0)
            if (ret_val == -1):
                continue
            elif (ret_val == -404):
                continue

main()
