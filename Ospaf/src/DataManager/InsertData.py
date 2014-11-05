'''
Insert items into database

@author: Garvin
'''
import MySQLdb
import ConnData

def InsertData(TableName,dic):
  if type(dic)==dict: 
   try:
    conn=ConnData.ConnData()
    cur=conn.cursor()
    COLstr=''
    ROWstr=''
    
    ColumnStyle=' VARCHAR(20)'
    for key in dic.keys():
         COLstr=COLstr+' '+key+ColumnStyle+','    
         ROWstr=(ROWstr+'"%s"'+',')%(dic[key])

    #IF THE TABLE HAS ALREADY EXICTE
    try:
      cur.execute("SELECT * FROM  %s"%(TableName))
      cur.execute("INSERT INTO %s VALUES (%s)"%(TableName,ROWstr[:-1]))
      
    except MySQLdb.Error,e:             
      cur.execute("CREATE TABLE %s (%s)"%(TableName,COLstr[:-1]))
      cur.execute("INSERT INTO %s VALUES (%s)"%(TableName,ROWstr[:-1]))
    conn.commit()
    cur.close()
    conn.close()
   except MySQLdb.Error,e:
      print "Mysql Error %d: %s" % (e.args[0], e.args[1])        
  else:
     if type(dic)==list:
         try:
          conn=ConnData.ConnData()
          cur=conn.cursor()
          try:
               cur.execute("SELECT * FROM  %s"%(TableName))
               for item in dic:
                     cur.execute("INSERT INTO %s VALUES ('%s')"%(TableName,item))
      
          except MySQLdb.Error,e:             
               cur.execute("CREATE TABLE %s (url VARCHAR(100))"%(TableName))
               for item in dic:
                     cur.execute("INSERT INTO %s VALUES ('%s')"%(TableName,item))
          
          conn.commit()
          cur.close()
          conn.close()
         except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])  
    
    
if __name__=='__main__':
    dic={"a":"b","c":"d"}
    list1=['b','c']
    InsertData('testtable',dic)
          
    InsertData('testtable1',list1)  