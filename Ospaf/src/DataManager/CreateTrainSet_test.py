'''
Create train set (temporary)
@author: Garvin
'''
import GetUrl
import InsertData
import GetFromData
import random
import GetRepoInfo

def GetUrlList():
    TableName='GitUrl'
    InsertData.InsertData(TableName, GetUrl.GetUrl(1050))
     


def GetNegaTrainSet():
    sample = random.sample(GetFromData.GetDataURL('GitUrl'), 50)
    for i in sample:
        InsertData.InsertData('GitTrainSet', GetRepoInfo.GetNegativeRepoInfo(i))

def GetPositiveTrainSet():       
#      RepoList=['adobe/adobe.github.com','twitter/twitter.github.com','gabrielecirulli/2048','ellisonleao/clumsy-bird','nikolaypavlov/MLPNeuralNet','ryanb/ruby-warrior','ipython/ipython','sympy/sympy'] 
     RepoList=['nikolaypavlov/MLPNeuralNet','ryanb/ruby-warrior','ipython/ipython','sympy/sympy'] 
     UrlList=[]
     for i in RepoList:
         UrlList.append('https://api.github.com/repos/'+i)
     for j in UrlList:
        InsertData.InsertData('GitTrainSet', GetRepoInfo.GetPositiveRepoInfo(j))    
         
# if __name__=='__main__':        
# #     GetUrlList() 
#      GetPositiveTrainSet()
# #     GetNegaTrainSet()
   
   