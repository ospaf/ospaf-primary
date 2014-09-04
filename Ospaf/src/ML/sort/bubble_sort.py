'''
Created on 2014.9.3

@author: Garvin
'''

def bubble_sort(list):
    dist=len(list)
    for j in range(0,dist):
        for i in range(0,dist-1):
            if list[i]>list[i+1]:
                t=list[i]
                list[i]=list[i+1]
                list[i+1]=t
    return list

if __name__ == '__main__':
    list=[52,46,2,7584,542]
    print bubble_sort(list)             