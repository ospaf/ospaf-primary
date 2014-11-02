'''
function:log(1+x)
the base is 'e'
'''
from numpy import *

def sig(mat):
  
     return (1.0/(1+exp(-mat)))
  # else:	
  #  dataMat=mat
  #  m,n = shape(dataMat)
  #  for i in range(m):
  #   	for j in range(n):
  #   		dataMat[i][j]=(1.0/(1+exp(-dataMat[i][j])))
  #  return dataMat



#print sig(dataMat)
