# -*- coding: utf-8 -*-
'''
Created on 2014年11月4日

@author: zhanghb
'''
import json
import urllib2
from DataConvert import DataManager
from copy import deepcopy
def TimeListSort(TimeList):
    Result=[]
    InputList=[]
    for item in TimeList:
        if item[-1]=='y':
            InputList.append((int(filter(str.isdigit,item)))*365)
        elif item[-1]=='m':
            InputList.append((int(filter(str.isdigit,item)))*30)
        elif item[-1]=='w':
            InputList.append((int(filter(str.isdigit,item)))*7)
        elif item[-1]=='d':
            InputList.append((int(filter(str.isdigit,item))))
        else:
            print "Input Format Error"
            break
    SortedList=deepcopy(InputList)
    Result.append(InputList)
    SortedList.sort()
    Result.append(SortedList)
    return Result

def div_CommitSum(url,*TimeList):
    url_data = urllib2.urlopen(url).readline()
    json_r=json.loads(url_data)
    SortedList=[]
    UnSortedList=[]
    CommitNum=[]
    
    if not TimeList:
        UnSortedList=[30,90,180]
        SortedList=[30,90,180]
    else:
        temp=TimeListSort(TimeList)
        UnSortedList=temp[0]
        SortedList=temp[1]
    CommitNum=[0]*len(SortedList)
    for item in json_r:
        DaysFromNow=DataManager(item[u'commit'][u'committer'][u'date'])
        if DaysFromNow<=SortedList[0]:
            CommitNum[UnSortedList.index(SortedList[0])]+=1
        else:
            for i in range(1,len(SortedList)):
                if (DaysFromNow>SortedList[i-1]) and (DaysFromNow<=SortedList[i]):
                    CommitNum[UnSortedList.index(SortedList[i])]+=1
                else:
                    pass
    return  CommitNum 
def total_CommitSum(url,*TimeList):
    url_data = urllib2.urlopen(url).readline()
    json_r=json.loads(url_data)
    SortedList=[]
    UnSortedList=[]
    CommitNum=[]
    
    if not TimeList:
        UnSortedList=[30,90,180]
        SortedList=[30,90,180]
    else:
        temp=TimeListSort(TimeList)
        UnSortedList=temp[0]
        SortedList=temp[1]
    CommitNum=[0]*len(SortedList)
    for item in json_r:
        DaysFromNow=DataManager(item[u'commit'][u'committer'][u'date'])
        for i in range(0,len(SortedList)):
            if DaysFromNow<=SortedList[i]:
                CommitNum[UnSortedList.index(SortedList[i])]+=1
            else:
                pass
    return  CommitNum    