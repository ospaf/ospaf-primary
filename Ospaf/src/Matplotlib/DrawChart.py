'''
use matplot to draw some charts
@author: Garvin
'''
import matplotlib.pyplot as plt

def BarChart(name,num):
    plt.bar(range(len(num)), num, align='center')
    plt.xticks(range(len(num)), name, size='large')
    plt.show()
    
    