import numpy as np
import matplotlib.pyplot as plt
import random
# from Datacreat import Dataprocess
import pandas as pd

def insert_city(distmatrix,route,city):
      min_increase = float('inf')
      best_position = None
      for i in range(len(route) + 1):
         if i ==0:
          increase =distmatrix[city][route[i]]
         elif i ==len(route):
            increase =distmatrix[route[i-1]][city]
         else:
             increase =distmatrix[route[i-1]][city]+distmatrix[city][route[i]]-distmatrix[route[i-1]][route[i]]
         if increase < min_increase:
                 min_increase = increase
                 best_position = i 
      return route[:best_position] + [city] + route[best_position:]
def population(numsalesman,positions,numsolution,distmatrix):
    initialsolu=[]
    numdepots=len(positions)
    while len(initialsolu) < numsolution:
            solution=[]
            unassigned=[i for i in range(numdepots)]#生成未指定的城市
            for i in range(numsalesman):
                subsolution=[]
                rd=random.choice(unassigned)#先给每个震源车所在路线均匀随机分配一个城市
                subsolution.append(rd)
                solution.append(subsolution)
                unassigned.remove(rd)
            num=len(unassigned)
            for l in range(num):
                k=np.random.randint(0,numsalesman)
                urd=random.choice(unassigned)
                #print(solution[k])
                solution[k]=insert_city(distmatrix,solution[k], urd)
                unassigned.remove(urd)
            if solution not in initialsolu:
                initialsolu.append(solution)
    return initialsolu

