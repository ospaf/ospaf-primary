# This is used to generate one file with all 'login' from different txts
# For example, we have 1.txt, 2.txt and the etc. each of them is came from
#   something like    https://api.github.com/users?since=100
# Finally, we will get a file like
#    initlove
#    fake_initlove
#    fake_initlove1
#
#
# The generated file is the most important, since what we get from '*since' is
#    not really helpful, only 'id-login' is good for the later usage.
#    
import base64
import json

from os import walk

for (dirpath, dirnames, filenames) in walk("./"):
    for file_txt in filenames:
        if (file_txt.find("txt") > 3):
            fo = open(file_txt, "r")
            str = fo.read(1000000)
            fo.close()
            val = json.loads(str)
            num = len(val)
            for item in val:
                print item["login"]
