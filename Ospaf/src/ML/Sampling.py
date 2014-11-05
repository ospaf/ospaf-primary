'''
Sampling archive

@author: Garvin 
'''
import random
def loadDataSet(fileName):      #general function to parse tab -delimited floats
    dataMat = []                #assume last column is target value
    fr = open(fileName)
    for line in fr.readlines():
        curLine = line.strip().split('\t')
#         fltLine = map(float,curLine) #map all elements to float()
        dataMat.append(curLine)
    return dataMat

def RandomSampling(dataMat,number):
    try:
         slice = random.sample(dataMat, number)    
         return slice
    except:
         print 'sample larger than population'

def RepetitionRandomSampling(dataMat,number):    
    sample=[]
    for i in range(number):
         sample.append(dataMat[random.randint(0,len(dataMat)-1)])
    return sample
def SystematicSampling(dataMat,number):    
    
       length=len(dataMat)
       k=length/number
       sample=[]     
       i=0
       if k>0 :       
         while len(sample)!=number:
            sample.append(dataMat[0+i*k])
            i+=1            
         return sample
       else :
         return RandomSampling(dataMat,number)   
       
            
# if __name__=='__main__':
#    dataMat=loadDataSet('/Users/hakuri/Desktop/data1.txt')
# #    print RandomSampling(dataMat,7)    
# #    RepetitionSampling(dataMat,4)
#    print SystematicSampling(dataMat,9)