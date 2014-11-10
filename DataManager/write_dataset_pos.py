
import GetRepoInfo
import re
import sys
import os
sys.path.append("..")
import config

def Insert_pos_data(data_num):    
    fr1=open(config.dataset_root+'/dataset.txt','a')
    j=0
    positive_repo=config.pos_repo
    for i in positive_repo:
        print i
        if j<data_num:
          dic={}
          dic=GetRepoInfo.GetRepoInfo('https://api.github.com/repos/'+i.strip())          
          key_list=config.feat
          text=''
          for k in key_list:
            text=text+str(dic[k])+'\t'
          print text  
          fr1.write(text+'1'+'\n')  
          j+=1
        else:
          break
        
              
Insert_pos_data(5)        
