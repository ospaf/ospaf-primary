'''
The first section test (temporary)
@author: Garvin
'''
import DataManager.GetFromData
import ML.AutoNorm
import ML.LR
import Matplotlib.DrawChart
import DataManager.GetFromData
import DataManager.GetRepoInfo
import DataManager.InsertData

def AutoNormData():
    dataMat,labelMat=DataManager.GetFromData.GetDataRepo('TrainSet')
    dataMat=ML.AutoNorm.AutoNorm(dataMat)
    return dataMat,labelMat

def AddConstant():
    dataMat,labelMat=AutoNormData()
    LRMat=[]
    list=[1]#add constant item to LRMat
    for i in dataMat:
        LRMat.append(list+i)  
    return LRMat,labelMat

def GetPreSet():
     RepoList=['gilt/gilt.github.com','Shopify/shopify.github.com','gousiosg/github-mirror','jimenbian/DataMining'] 
     UrlList=[]
     RepoInfo={}
     for i in RepoList:
         UrlList.append('https://api.github.com/repos/'+i)
     for j in UrlList:
         DataManager.InsertData.InsertData('PreSet', DataManager.GetRepoInfo.GetRepoInfo(j))
     
     

if __name__=='__main__':  
     LRMat,labelMat=AddConstant()
     weight=ML.LR.GetResult(LRMat, labelMat)
     dataMat,dataLable=DataManager.GetFromData.GetDataRepo1('preset1')
     list=[1]#add constant item to LRMat
     LRMat1=ML.AutoNorm.AutoNorm(dataMat) 
     
     LRMat2=[]
     for i in LRMat1:
       LRMat2.append(list+i)
     print LRMat2
     print weight 
     print  LRMat2*weight
#     print weight
#     nameMat=myarr=['constant','star','fork','watcher','issues','size','created_at','pushed_at','updated_at']
     name= DataManager.GetFromData.GetProjectName('preset1')
     Matplotlib.DrawChart.BarChart(name, LRMat2*weight)
      
    