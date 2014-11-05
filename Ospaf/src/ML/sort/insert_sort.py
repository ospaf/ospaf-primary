'''
Created on 2014.9.1

@author: Garvin Li
'''

def insert_sort(list):
   
    for i in range(1,len(list)):
       key=list[i]
       j=i-1
       while j>=0 and key<list[j]:
             list[j+1]=list[j]
             j-=1
       list[j+1]=key
    return list           


if __name__ == '__main__':
    list=[52,46,2,7584,542]
    print insert_sort(list)
    