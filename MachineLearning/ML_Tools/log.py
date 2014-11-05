'''
function:log(1+x)
the base is 'e'
'''
from numpy import *

def loge(mat):
  if type(mat)==dict:
    for k,v in mat.iteritems():
    	if k=='name':
    		pass
    	else:
    	  mat[k]=log(float(v)+1)	
    return mat	  

  else: 	
    dataMat = []
    dataMat=mat
    m,n = shape(dataMat)
    weights = ones((m,n))
    print 'beging progress log(1+x)'
    return log(dataMat+weights)
