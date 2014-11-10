
import GetRepoInfo
import re
import sys
import os
sys.path.append("..")
import config

def Insert_neg_data(data_num):
    fr=open(config.dataset_root+'/url.txt') 
    fr1=open(config.dataset_root+'/dataset.txt','a')
    j=0
    for i in fr.readlines():
        print i
        if j<data_num:
          dic={}
          dic=GetRepoInfo.GetRepoInfo(i.strip())
          #print dic
          key_list=config.feat
          text=''
          for k in key_list:
            text=text+str(dic[k])+'\t'
          print text  
          fr1.write(text+'0'+'\n')  
          j+=1
        else:
          break
        
              
Insert_neg_data(5)        
