'''
logistic regression
@author: Garvin
'''

from numpy import *
import sys
import os
sys.path.append("..")
import config
import ML_Tools.log
import ML_Tools.AutoNorm

def loadDataSet():
    dataMat = []; labelMat = []
    fr=open(config.dataset_root+'/dataset.txt') 
    for line in fr.readlines():
        lineArr = line.strip().split()
        dataMat.append([1,float(lineArr[1]), float(lineArr[2]),float(lineArr[3]),float(lineArr[4]),float(lineArr[5]),float(lineArr[6]),float(lineArr[7]),float(lineArr[8]),float(lineArr[9]),float(lineArr[10]),float(lineArr[11]),float(lineArr[12]),float(lineArr[13]),float(lineArr[14]),float(lineArr[15]),float(lineArr[16]),float(lineArr[17]),float(lineArr[18]),float(lineArr[19]),float(lineArr[20]),float(lineArr[21]),float(lineArr[22]),float(lineArr[23])])
        labelMat.append(int(lineArr[24]))
    dataMat=ML_Tools.log.loge(dataMat)
    #dataMat=ML_Tools.AutoNorm.AutoNorm(dataMat)
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
    

     
if __name__=='__main__':
    dataMat,labelMat=loadDataSet()
    weight=GetResult( dataMat,labelMat)

    