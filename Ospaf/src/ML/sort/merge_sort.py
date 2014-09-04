'''
Created on 2014.9.3

@author: Garvin

attention:only even number
'''

def merger_sort(list,first,last):
    if first+1<last:
        mid=(first+last)/2
        merger_sort(list,first,mid)
        merger_sort(list,mid,last)
        merger(list,first,mid,last)
    return list    
    

def merger(list,first,mid,last):
    indexA=first
    indexB=mid
    list_tmp=[]
    i=0
    while indexA<mid and indexB<last:
        if list[indexA]<list[indexB]:
            list_tmp[i]=list[indexA]
            i+=1
            indexA+=1
       
        else :           
            list_tmp[i]=list[indexB]
            i+=1
            indexB+=1     
    
    while  indexA<mid:
        list_tmp[i]=list[indexA]
        indexA+=1
   
    while  indexB<last:
        list_tmp[i]=list[indexB]
        indexB+=1
    return  list_tmp         
            
if __name__ == '__main__':
    list=[52,46,2,7584,542,523]
    print merger_sort(list,0,5) 
        
        
        
    