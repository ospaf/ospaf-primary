'''
Manage the data-feature information
@author: Garvin
'''
import time
def DataManager(data):
    now=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    dyear=int(now[:4])-int(data[:4])
    dmonth=int(now[5:7])-int(data[5:7])
    ddata=int(now[8:10])-int(data[8:10])
    distance=dyear*360+dmonth*30+ddata
   
    return distance




# if __name__=='__main__':    
#     a=2008-01-15T05:42:45Z
#     print DataManager(a)