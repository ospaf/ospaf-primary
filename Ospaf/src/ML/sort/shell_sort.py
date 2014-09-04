'''
Created on 2014.9.1

@author: Garvin
'''
  
def shell_sort(list):  
    dist=len(list)/2 

    while dist>0:  
        for i in range(dist,len(list)):  
            tmp=list[i]  
            j=i  
            while j>=dist and tmp<list[j-dist]:  
                list[j]=list[j-dist]  
                j-=dist  
            list[j]=tmp  
        dist/=2 
    return list    

if __name__ == '__main__':
    list=[52,46,2,7584,542]
    print shell_sort(list)