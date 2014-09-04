'''
get the url of the repos from githubapi

@author: Garvin
'''
import re
import os

def GetUrl(num):
    str = os.popen("curl -G https://api.github.com/repositories?since=%d"%(num)).read()
    pattern = '"url"'
    pattern1='repos'
    urls=str.split(',\n')
    list=[]         
    for i in urls:
      if pattern in i and pattern1 in i:
           
#          text1=i.splite(':')
          text=re.compile('"(.*?)"').findall(i)[1]
          list.append(text)
    return list      


# 
# if __name__=='__main__':
# #      str = os.popen("curl -G https://api.github.com/repositories?since=50").read()
#        print GetUrl(50)
#      