'''
get information of the repo

@author: Garvin
'''
import os
import json
import FeatureManager.DataManager
import GL

def GetRepoInfo(str):
     Info= os.popen("curl -G %s"%(str)).read()
     json_r=json.loads(Info)
     Jdict = {} 
     myarr=GL.features
     
     Jdict[myarr[0]]=json_r.get('name')
     Jdict[myarr[1]]=json_r.get('size')
     Jdict[myarr[2]]=json_r.get('stargazers_count')
     Jdict[myarr[3]] =json_r.get('watchers_count')
     Jdict[myarr[4]]=json_r.get('forks_count')
     Jdict[myarr[5]]=json_r.get('open_issues')
     created_at= FeatureManager.DataManager.DataManager(json_r.get('created_at'))
     pushed_at= FeatureManager.DataManager.DataManager(json_r.get('pushed_at'))
     updated_at= FeatureManager.DataManager.DataManager(json_r.get('updated_at'))
     Jdict[myarr[6]]=created_at
     Jdict[myarr[7]]=pushed_at
     Jdict[myarr[8]]=updated_at
     return Jdict
 
def GetPositiveRepoInfo(str):
     Info= os.popen("curl -G %s"%(str)).read()
     json_r=json.loads(Info)
     Jdict = {} 
     myarr=GL.features
     
     Jdict[myarr[0]]=json_r.get('name')
     Jdict[myarr[1]]=json_r.get('size')
     Jdict[myarr[2]]=json_r.get('stargazers_count')
     Jdict[myarr[3]] =json_r.get('watchers_count')
     Jdict[myarr[4]]=json_r.get('forks_count')
     Jdict[myarr[5]]=json_r.get('open_issues')
     created_at= FeatureManager.DataManager.DataManager(json_r.get('created_at'))
     pushed_at= FeatureManager.DataManager.DataManager(json_r.get('pushed_at'))
     updated_at= FeatureManager.DataManager.DataManager(json_r.get('updated_at'))
     Jdict[myarr[6]]=created_at
     Jdict[myarr[7]]=pushed_at
     Jdict[myarr[8]]=updated_at
     Jdict['label']=1
     return Jdict 

def GetNegativeRepoInfo(str):
     Info= os.popen("curl -G %s"%(str)).read()
     json_r=json.loads(Info)
     Jdict = {} 
     myarr=GL.features     
     Jdict[myarr[0]]=json_r.get('name')
     Jdict[myarr[1]]=json_r.get('size')
     Jdict[myarr[2]]=json_r.get('stargazers_count')
     Jdict[myarr[3]] =json_r.get('watchers_count')
     Jdict[myarr[4]]=json_r.get('forks_count')
     Jdict[myarr[5]]=json_r.get('open_issues')
     created_at= FeatureManager.DataManager.DataManager(json_r.get('created_at'))
     pushed_at= FeatureManager.DataManager.DataManager(json_r.get('pushed_at'))
     updated_at= FeatureManager.DataManager.DataManager(json_r.get('updated_at'))
     Jdict[myarr[6]]=created_at
     Jdict[myarr[7]]=pushed_at
     Jdict[myarr[8]]=updated_at
     Jdict['label']=0
     return Jdict 


# print GetPositiveRepoInfo('https://api.github.com/repos/adobe/adobe.github.com')

