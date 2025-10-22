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
#读取数据并处理
# path = r'data\example03.csv'
# data=pd.read_csv(path,usecols=['Vibrator', 'ActualX','ActualY'])#读取震源车以及炮点坐标列
# first_x_rows = data.head(400)
# positions=first_x_rows[['ActualX','ActualY']]
# X = positions['ActualX'].tolist()
# Y= positions['ActualY'].tolist()
# position=np.column_stack((X,Y))
# #产生需要的距离矩阵
# Data=Dataprocess(position)
# distmatrix=Data.build_dist_mat()#产生距离矩阵
# numdepots=len(first_x_rows)                                                                                                                       
np.random.seed(0)
#模拟实验
position=np.load('position50.npy')#这个是随机生成的一组坐标，也在压缩包里面

print('接下来50')
np.random.shuffle(position) 
Data=Dataprocess(position)

distmatrix=Data.build_dist_mat()
#使用遗传算法的nsga2
numsolution=20#初始种群
numsalesman=4#实际数据前x行的震源车数
everyworktime=20#震源车在每个炮点的激发时间，假设是固定的
velocity=8.33#震源车移动速度
solution=population(numsalesman, position, numsolution, distmatrix)
def main_nsga2(numsolution,numsalesman,everyworktime,velocity,numgeneration,distmatrix):
    #产生numsolution个mtsp初始解
    
    
    #对初始解进行遗传操作,产生numsolution个子代
    # Cost = Evaluator_solution(initialsolution,numsalesman)
    # totalcostini =Cost.totalcost(distmatrix, everyworktime, velocity,'disteverysolution')
    # print(totalcostini)
    initialsolution=population(numsalesman, position, 2*numsolution, distmatrix)
    # # #锦标赛选择numsolution/2个初始解进入交配池
    # pool=tournamentselection(initialsolution, numsolution,3,totalcost)
    Gga=GGA(distmatrix)
    # q_0=Gga.gga(initialsolution,0.8,0.8,0.67,numsolution)
    #合并初始解和初始子代
   
    #将R_0非支配排序并计算拥挤度
    data0=np.zeros(numgeneration)#用于画收敛图
    data1=np.zeros(numgeneration)
    dist_cost_cache = {}
    time_cost_cache = {}
    # 计算初始解的成本并缓存
    initial_cost = Evaluator_solution(initialsolution, numsalesman)
    initial_costs = initial_cost.totalcost(distmatrix, everyworktime, velocity, 'disteverysolution')
    initial_dist_costs, initial_time_costs = initial_costs
    for solution, dist_cost, time_cost in zip(initialsolution, initial_dist_costs, initial_time_costs):
        solution_tuple = tuple(map(tuple, solution))
        dist_cost_cache[solution_tuple] = dist_cost
        time_cost_cache[solution_tuple] = time_cost
        
    r_0=initialsolution  
    for g,_ in enumerate(tqdm.tqdm(range(numgeneration))):
        #做一个缓存，避免对同一个解重复计算成本
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
        #把Ft按照拥挤度排序
        #先把Ft元素的拥挤度提出来
        crowdedFt=np.array([crowddistance[idx] for idx in front[t]])
        #按照拥挤度排序
        sorted_indices = np.argsort(-crowdedFt)[:numsolution - len(p_t)]
        p_t.extend(r_0[front[t][idx]] for idx in sorted_indices)
        #遗传操作
        #对解进行遗传操作,产生numsolution个子代
        q_t=Gga.gga(p_t,0.8,0.8,0.62,numsolution)
        #用于画收敛图并挑出最佳子代
       
        #合并初始解和初始子代
        r_0=q_t+p_t
        if g==0:
            solu0=q_t[0]
       
    return q_t,data0,data1,solu0


# unique_values =first_x_rows['Vibrator'].drop_duplicates()
# a=[]
# for i in unique_values:
#   specified_rows_index = first_x_rows.loc[first_x_rows['Vibrator'] == i].index
#   a.append(list(specified_rows_index))
# solu=[]
# solu.append(a)

numgeneration=50#迭代数
# Cost=Evaluator_solution(solu, numsalesman)
# realtotal=Cost.totalcost(distmatrix, everyworktime,velocity,'disteverysolution')

qt,data00,data11,solu0=main_nsga2(numsolution, numsalesman, everyworktime, velocity, numgeneration, distmatrix)
Cost = Evaluator_solution(qt,numsalesman)
totalcost =Cost.totalcost(distmatrix, everyworktime, velocity,'disteverysolution')
Sort=Non_domination_sort(qt,totalcost)
front,frontfrank=Sort.non_domination_sort()
bestroute=qt[front[0][0]] 
Cost2=Evaluator_solution([bestroute],numsalesman)   
mytotal=Cost2.totalcost(distmatrix, everyworktime,velocity,'disteverysolution')
# if mytotal[0]<realtotal[0] and mytotal[1]<realtotal[1]:
#     print('True')
from matplotlib import rcParams
config = {
        "font.family": 'serif',
        "mathtext.fontset": 'stix',
        "font.serif": ['SimSun'],  
        'axes.unicode_minus': False  
    }
rcParams.update(config)

plt.plot(data00,marker='.', linestyle='-')
plt.xlabel('Iter')
plt.ylabel('Distance')
# plt.title('Convergence Plot1 of NSGGA-II')
plt.grid(True)
plt.show()
plt.plot(data11, marker='.', linestyle='-',color='red')
plt.xlabel('Iter')
plt.ylabel('Time with TD Model')
# plt.title('Convergence Plot2 of NSGGA-II')
plt.grid(True)
plt.show()

x_coords = [point[0] for point in position]
y_coords = [point[1] for point in position]
# 绘制炮点初始
plt.scatter(x_coords, y_coords,marker='.', color='black')
for idx, route in enumerate(solution[0]):
    route_coords_x = [position[i][0] for i in route ] 
    route_coords_y = [position[i][1] for i in route]
    plt.plot(route_coords_x, route_coords_y, label=f'Route {idx + 1}')
# 设置标题和标签

plt.xlabel('X')
plt.ylabel('Y')
# 显示网格和图例
plt.grid(True)
# 显示图形
plt.show()


x_coords = [point[0] for point in position]
y_coords = [point[1] for point in position]
# 绘制炮点
plt.scatter(x_coords, y_coords,marker='.', color='black')
# 绘制路线
for idx, route in enumerate(solu0):
    route_coords_x = [position[i ][0] for i in route ] # 炮点从1开始编号
    route_coords_y = [position[i ][1] for i in route]
    plt.plot(route_coords_x, route_coords_y, label=f'Route {idx + 1}')

# 设置标题和标签

plt.xlabel('X')
plt.ylabel('Y')
# 显示网格和图例
plt.grid(True)
# 显示图形
plt.show()


x_coords = [point[0] for point in position]
y_coords = [point[1] for point in position]
# 绘制炮点
plt.scatter(x_coords, y_coords,marker='.', color='black')
# 绘制路线
for idx, route in enumerate(bestroute):
    route_coords_x = [position[i ][0] for i in route ] # 炮点从1开始编号
    route_coords_y = [position[i ][1] for i in route]
    plt.plot(route_coords_x, route_coords_y, label=f'Route {idx + 1}')

# 设置标题和标签

plt.xlabel('X')
plt.ylabel('Y')
# 显示网格和图例
plt.grid(True)
# 显示图形
plt.show()

distance_costs = totalcost[0]
time_costs = totalcost[1]

# 创建散点图
  # 示例 Pareto 前沿索引
pareto_front = np.array(front[0])

# 对 Pareto 最优解按距离成本排序
sorted_pareto = pareto_front[np.argsort(distance_costs[pareto_front].flatten())]

# 绘制所有解的散点图
plt.scatter(distance_costs, time_costs, color='blue', label='All solutions')

# 绘制 Pareto 最优解的散点图
plt.scatter(distance_costs[sorted_pareto], time_costs[sorted_pareto], color='red', label='Pareto Front solution')

# 绘制 Pareto 前沿
plt.plot(distance_costs[sorted_pareto], time_costs[sorted_pareto], color='red', linestyle='--')

# 添加标题和标签
plt.title('Pareto-optimal front')
plt.xlabel('Distance')
plt.ylabel('Time')                      
plt.legend()



    
  