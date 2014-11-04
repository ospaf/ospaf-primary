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

def write_model(dic):
  fr=open(config.dataset_root+'/model.txt','w')  
  for i in config.model_feat:
    fr.write(i+'\t'+str(dic[i])+'\n')
  fr.close()

if __name__ == '__main__':
  write_model(get_model())


  

