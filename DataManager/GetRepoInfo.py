from __future__ import division
import os
import sys
import json
sys.path.append("..")
import config
import DM_Tools.DataConvert
import DM_Tools.Contributor_Count
import DM_Tools.ExtractCommitter


def GetRepoInfo(str):
     Info= os.popen("curl -G %s"%(str)).read()
     json_r=json.loads(Info)
     Jdict = {} 
     commits_result=[]
     commits_result=DM_Tools.ExtractCommitter.total_CommitSum(str+'/commits')
     myarr=config.feat
    
     Jdict[myarr[0]]=json_r.get('name')
     Jdict[myarr[1]]=json_r.get('size')
     Jdict[myarr[2]]=json_r.get('stargazers_count')
     Jdict[myarr[3]] =json_r.get('watchers_count')
     Jdict[myarr[4]]=json_r.get('forks_count')
     Jdict[myarr[5]]=json_r.get('open_issues')
     created_at= DM_Tools.DataConvert.DataManager(json_r.get('created_at'))
     pushed_at= DM_Tools.DataConvert.DataManager(json_r.get('pushed_at'))
     updated_at= DM_Tools.DataConvert.DataManager(json_r.get('updated_at'))
     Jdict[myarr[6]]=created_at
     Jdict[myarr[7]]=pushed_at
     Jdict[myarr[8]]=updated_at
     Jdict[myarr[9]]=DM_Tools.Contributor_Count.get_number(json_r.get('contributors_url'))
     #feat=['name','size','star','watcher','fork','issues','created_at','pushed_at','updated_at','contributors','created_atDstar','created_atDwatcher','created_atDfork','created_atDissues','created_atDsize','created_atDcontributors','starDfork','starDissues','starDsize','starDcontributors','forkDissues','forkDsize','forkDcontributors','sizeDcontributors']
     Jdict['created_atDstar']=int(Jdict['created_at'])/(int(Jdict['star'])+1)
     Jdict['created_atDwatcher']=int(Jdict['created_at'])/(int(Jdict['watcher'])+1)
     Jdict['created_atDfork']=int(Jdict['created_at'])/(int(Jdict['fork'])+1)
     Jdict['created_atDissues']=int(Jdict['created_at'])/(int(Jdict['issues'])+1)
     Jdict['created_atDsize']=int(Jdict['created_at'])/(int(Jdict['size'])+1)
     Jdict['created_atDcontributors']=int(Jdict['created_at'])/(int(Jdict['contributors'])+1)
     Jdict['starDfork']=int(Jdict['star'])/(int(Jdict['fork'])+1)
     Jdict['starDissues']=int(Jdict['star'])/(int(Jdict['issues'])+1)
     Jdict['starDsize']=int(Jdict['star'])/(int(Jdict['size'])+1)
     Jdict['starDcontributors']=int(Jdict['star'])/(int(Jdict['contributors'])+1)
     Jdict['forkDissues']=int(Jdict['fork'])/(int(Jdict['issues'])+1)
     Jdict['forkDsize']=int(Jdict['fork'])/(int(Jdict['size'])+1)
     Jdict['forkDcontributors']=int(Jdict['fork'])/(int(Jdict['contributors'])+1)
     Jdict['sizeDcontributors']=int(Jdict['size'])/(int(Jdict['contributors'])+1)
     Jdict['month_1_commit']=int(commits_result[0])
     Jdict['month_3_commit']=int(commits_result[1])
     Jdict['month_6_commit']=int(commits_result[2])
     return Jdict


print GetRepoInfo('https://api.github.com/repos/jimenbian/DataMining')