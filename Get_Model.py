import config
from MachineLearning.LR import *

def get_model():
  dataMat,labelMat=loadDataSet()
  weight=GetResult(dataMat,labelMat)
  print weight
  list_weight=[]
  dic_weight={}
  m,n=shape(weight)
  #print m,n
  
  for i in range(m):
     dic_weight[config.feat[i]]=float(weight[i][0])
  dic_weight['constant']=  float(weight[0][0])
  return dic_weight

  

