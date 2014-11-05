'''
Get data from database,convert from str to int

@author: Garvin
'''

import MySQLdb
import re
from numpy import *
import ConnData

def GetDataURL(tablename):
 try:
    conn=ConnData.ConnData()
    cur=conn.cursor()       
    cur.execute("SELECT * FROM %s"%(tablename))
    results=cur.fetchall()
    URLlist=[]
    for r in results:
       
          URLlist.append(r[0])
    return URLlist      
    conn.commit()
    cur.close()
    conn.close()
 except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def GetDataRepo(tablename):
 try:
    conn=ConnData.ConnData()
    cur=conn.cursor()       
    cur.execute("SELECT * FROM %s"%(tablename))
    results=cur.fetchall()
    dataMat = []; labelMat = []
    list1=[1]#the constant equal 1
    for i in results:
#         dataMat.append(map(int, i[1:-1]))
        dataMat.append(map(int, i[1:-1]))
        labelMat.append(int(i[-1]))  
    
    
    conn.commit()
    cur.close()
    conn.close()
    return dataMat,labelMat
 except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def GetProjectName(tablename):
 try:
    conn=ConnData.ConnData()
    cur=conn.cursor()       
    cur.execute("SELECT * FROM %s"%(tablename))
    results=cur.fetchall()
    nameMat = []
    list1=[1]#the constant equal 1
    for i in results:
        nameMat.append(i[0])
        
    
     
    conn.commit()
    cur.close()
    conn.close()
    return nameMat
 except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
# GetDataRepo('TrainSet')
 
 
 
def GetDataRepo1(tablename):
 try:
    conn=ConnData.ConnData()
    cur=conn.cursor()       
    cur.execute("SELECT * FROM %s"%(tablename))
    results=cur.fetchall()
    dataMat = []; labelMat = []
    list1=[1]#the constant equal 1
    for i in results:
#         dataMat.append(map(int, i[1:-1]))
        dataMat.append(map(int, i[1:]))
        labelMat.append(int(i[-1]))  
    
    
    conn.commit()
    cur.close()
    conn.close()
    return dataMat,labelMat
 except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
 