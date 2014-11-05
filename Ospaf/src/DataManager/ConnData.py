'''
Define the key of database
@author: Garvin
'''
import MySQLdb

def ConnData():
    conn=MySQLdb.connect(host='localhost',user='root',passwd='tiancailibo',db='test',port=3306)
    return conn