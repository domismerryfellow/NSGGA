import numpy as np
import matplotlib.pyplot as plt
from Datacreat import Dataprocess
from Evaluator import Evaluator_solution
from Nondominationsort import Non_domination_sort
from GGASS import GGA
from new import population
import pandas as pd
import tqdm
import time
import random                                                                                                         
np.random.seed(0)
np.random.shuffle(position) 
Data=Dataprocess(position)
distmatrix=Data.build_dist_mat()
#使用遗传算法的nsga2
numsolution=20#初始种群
numsalesman=4#震源车数
everyworktime=20#震源车在每个炮点的激发时间
velocity=8.33#震源车移动速度
solution=population(numsalesman, position, numsolution, distmatrix)

def main_nsga2(numsolution,numsalesman,everyworktime,velocity,numgeneration,distmatrix):
    data0=np.zeros(numgeneration)
    data1=np.zeros(numgeneration)
    dist_cost_cache = {}
    time_cost_cache = {}
    initial_cost = Evaluator_solution(initialsolution, numsalesman)
    initial_costs = initial_cost.totalcost(distmatrix, everyworktime, velocity, 'disteverysolution')
    initial_dist_costs, initial_time_costs = initial_costs
    for solution, dist_cost, time_cost in zip(initialsolution, initial_dist_costs, initial_time_costs):
        solution_tuple = tuple(map(tuple, solution))
        dist_cost_cache[solution_tuple] = dist_cost
        time_cost_cache[solution_tuple] = time_cost
        
    r_0=initialsolution  
    for g,_ in enumerate(tqdm.tqdm(range(numgeneration))):
        cached_costs_dist =np.zeros(len(r_0))
        cached_costs_time =np.zeros(len(r_0))
        uncached_solutions = []
        uncached_indices = []
        for idx, solution in enumerate(r_0):
            solution_tuple = tuple(map(tuple, solution))
            if solution_tuple in dist_cost_cache and solution_tuple in time_cost_cache:
                cached_costs_dist[idx]=dist_cost_cache[solution_tuple]
                cached_costs_time[idx]=dist_cost_cache[solution_tuple]
            else:
                uncached_solutions.append(solution)
                uncached_indices.append(idx)
        if uncached_solutions:
            Cost = Evaluator_solution(uncached_solutions, numsalesman)
            new_costs = Cost.totalcost(distmatrix, everyworktime, velocity, 'disteverysolution')
            new_dist_costs,new_time_costs = new_costs

            for solution, dist_cost, time_cost, idx in zip(uncached_solutions, new_dist_costs, new_time_costs, uncached_indices):
                solution_tuple = tuple(map(tuple, solution))
                dist_cost_cache[solution_tuple] = dist_cost
                time_cost_cache[solution_tuple] = time_cost
                cached_costs_dist[idx]=dist_cost_cache[solution_tuple]
                cached_costs_time[idx]=time_cost_cache[solution_tuple]
        totalcost = [cached_costs_dist, cached_costs_time]
        Sort=Non_domination_sort(r_0,totalcost)
        front,frontfrank=Sort.non_domination_sort()
        crowddistance =  Sort.crowding_distance(2)
        p_t=[]
        t=0
        data0[g] = np.min(totalcost[0])
        data1[g] = np.min(totalcost[1])
        #构建新的子代
        while len(p_t) + len(front[t]) <= numsolution:
            p_t.extend(r_0[idx] for idx in front[t])
            t += 1
        crowdedFt=np.array([crowddistance[idx] for idx in front[t]])
        #按照拥挤度排序
        sorted_indices = np.argsort(-crowdedFt)[:numsolution - len(p_t)]
        p_t.extend(r_0[front[t][idx]] for idx in sorted_indices)
        q_t=Gga.gga(p_t,0.8,0.8,0.62,numsolution)
        r_0=q_t+p_t
        if g==0:
            solu0=q_t[0]
       
    return q_t,data0,data1,solu0


numgeneration=50#迭代数
qt,data00,data11,solu0=main_nsga2(numsolution, numsalesman, everyworktime, velocity, numgeneration, distmatrix)
Cost = Evaluator_solution(qt,numsalesman)
totalcost =Cost.totalcost(distmatrix, everyworktime, velocity,'disteverysolution')
Sort=Non_domination_sort(qt,totalcost)
front,frontfrank=Sort.non_domination_sort()
bestroute=qt[front[0][0]] 
Cost2=Evaluator_solution([bestroute],numsalesman)   
mytotal=Cost2.totalcost(distmatrix, everyworktime,velocity,'disteverysolution')


    
  
