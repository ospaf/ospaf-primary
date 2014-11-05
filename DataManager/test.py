'''
get the url of the repos from githubapi

@author: Garvin
'''
import re
import os
import sys
sys.path.append("..")
import config
import GetRepoInfo

def GetUrl(num):
    fr=open(config.dataset_root+'/url.txt','a') 
    str = os.popen("curl -G https://api.github.com/repositories?since=%d"%(num)).read()
    pattern = '"url"'
    pattern1='repos'
    urls=str.split(',\n')
    list=[]
    j=0
             
    for i in urls:
      if j<3:
       if pattern in i and pattern1 in i:
          text=re.compile('"(.*?)"').findall(i)[1]
          
          print GetRepoInfo.GetRepoInfo(text)
          j+=1
          fr.write(text+'\n')
      else:
        break 
      fr.close()          
      break      


# 
if __name__=='__main__':
# #      str = os.popen("curl -G https://api.github.com/repositories?since=50").read()
        print GetUrl(50)
      