'''
Created on 2014.9.3

@author: Garvin
'''
  
def selection_sort(list):
      i=0
      j=0
      while i>=0 and i<=(len(list)-1):
          while j>=i and j<=(len(list)-1):          
            if list[i]>list[j]:
               t=list[i]
               list[i]=list[j]
               list[j]=t
            j+=1
          i+=1
          j=i      
      return list
  
if __name__ == '__main__':
    list=[52,46,2,7584,542]
    print selection_sort(list)       
               
          
