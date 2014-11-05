'''
logistic regression
@author: Garvin
'''
import matplotlib.pyplot as plt
from numpy import *


def loadDataSet():
    dataMat = []; labelMat = []
    fr = open('/Users/hakuri/Desktop/lr.txt')
    for line in fr.readlines():
        lineArr = line.strip().split()
        dataMat.append([1,float(lineArr[0]), float(lineArr[1]),float(lineArr[2])])
        labelMat.append(int(lineArr[2]))
    return dataMat,labelMat

def sigmoid(inX):
    return 1.0/(1+exp(-inX))

def gradAscent(dataMatIn, classLabels):
    dataMatrix = mat(dataMatIn)             #convert to NumPy matrix
    labelMat = mat(classLabels).transpose() #convert to NumPy matrix
    
    m,n = shape(dataMatrix)
    alpha = 0.001
    maxCycles = 500
    weights = ones((n,1))
    
    for k in range(maxCycles):              #heavy on matrix operations
        h = sigmoid(dataMatrix*weights)     #matrix mult    
        error = (labelMat - h)              #vector subtraction
        weights = weights + alpha * dataMatrix.transpose()* error #matrix mult
    return weights

def GetResult(dataMat,labelMat):
    
    weights=gradAscent(dataMat,labelMat)
    
    return weights
    
#     plotBestFit(weights)
   

def autoNorm(dataSet):
    minVals = dataSet.min(0)
    maxVals = dataSet.max(0)
    ranges = maxVals - minVals
    normDataSet = zeros(shape(dataSet))
  
    m = dataSet.shape[0]
    normDataSet = dataSet - tile(minVals, (m,1))
    #print normDataSet
    normDataSet = normDataSet/tile(ranges, (m,1)) #element wise divide
   # print normDataSet
    return normDataSet, ranges, minVals
    
def plotBestFit(dataMat,labelMat,weights):
     
    
    dataArr = array(dataMat)
    n = shape(dataArr)[0] 
    xcord1 = []; ycord1 = []
    xcord2 = []; ycord2 = []
    for i in range(n):
        if int(labelMat[i])== 1:
            xcord1.append(dataArr[i,1]); ycord1.append(dataArr[i,2])
        else:
            xcord2.append(dataArr[i,1]); ycord2.append(dataArr[i,2])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(xcord1, ycord1, s=30, c='red', marker='s')
    ax.scatter(xcord2, ycord2, s=30, c='green')
    x=arange(-3000.0,3000.0,0.1)
    y = (2.76955-66.45608*x)/(-6.83271)    
    ax.plot(x,y)
    plt.xlabel('X1'); plt.ylabel('X2');
    plt.show()    
     
if __name__=='__main__':
    dataMat,labelMat=loadDataSet()
    weight=GetResult( dataMat,labelMat)
    plotBestFit(dataMat,labelMat,weight)
    