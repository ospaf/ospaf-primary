from numpy import *

def test():
	dataMat = []

	dataMat=([e**2-1,7],[2,16],[5,1])
	m,n = shape(dataMat)
	weights = ones((m,n))
	print log(dataMat+weights)
test()