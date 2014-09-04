'''
compare the different word
@author: Garvin
'''
KeyWords=['add','remove','update']
commite=['Added testh ','removed fae gew','update cewf','add cek','get tawge']

def WordCompare(a,b):
    a_low=a.lower()
    b_low=b.lower()
    a_length=len(a_low)
    b_length=len(b_low)
    distance=min(a_length,b_length)   
    if distance%2 ==0:
        distance_cop=distance/2
    else:
        distance_cop=distance/2+1    
    for i in range(0,distance_cop):
        if a_low[i]==b_low[i]:
              continue
        else:
              return 0
              break   
    return 1

def GetKeyWordFreq(KeyWords,commits):
     WordFreqDic={}
     for i in KeyWords:
        WordFreqDic[i]=0
     for j in commite:
#         j.split()[0] 
        for key in WordFreqDic.keys():
            if  WordCompare(j.split()[0],key)==1:
                 WordFreqDic[key]=WordFreqDic[key]+1
     return WordFreqDic

          
    
if __name__=='__main__':
      print GetKeyWordFreq(KeyWords,commite)
#     print WordCompare('commited','commit')
