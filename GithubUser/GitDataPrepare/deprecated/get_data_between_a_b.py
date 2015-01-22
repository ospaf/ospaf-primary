# start to get user-lists from what you input
# limited to 9500000 in this case
# need to be improved since once it disconnected, 
# we have to reconnect it by hand.
#

import base64
import sys
import json
import urllib
import urllib2

user_pass = [
    {"user":"fake", "password": "fake", "count": 0}
]

def send_request(gh_user_id, i):
    url = "https://api.github.com/users?since="+`gh_user_id`+"&page_size=100";
    req = urllib2.Request(url)
    username = user_pass[i]["user"]
    password = user_pass[i]["password"]
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    req.add_header("Authorization", "Basic %s" % base64string)   
    user_pass[i]["count"] += 1

    res_data = urllib2.urlopen(req)
    res = res_data.read()
    text_file = open(`gh_user_id`+".txt", "w")
    text_file.write(res)
    text_file.close()

    val = json.loads(res)
    num = len(val)
    if (num <= 0):
        print req
        print res
        return -1
    else:
        return val[num-1]["id"]
 
def main():
    gh_len = len(sys.argv)
    if (gh_len >= 2):
        gh_user_id = long(sys.argv[1])
    else:
        gh_user_id = 0
        return -1

    i = 0
    while (i < 4):
        count = user_pass[i]["count"]
#        if (count >= 4990):
#            i += 1
#            continue

        new_user_id = send_request (gh_user_id, i)
        if (gh_len >= 3):
            limit = long(sys.argv[2]
            if (new_user_id > limit):
                break
        if (new_user_id > 0):
            print new_user_id
            gh_user_id = new_user_id
        else:
            i += 1

main()
