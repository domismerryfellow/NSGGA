
import numpy as np
import time
from TDtotaltime import TDtotaltime

#用于评估解的类
#主要是计算此解的路程成本和时间成本
class Evaluator_solution:
    def __init__(self,mtspsolution,numsalesman):#传入解集
     self.solution=mtspsolution
     self.numsalesman=numsalesman#震源车数目
     self.numsolution=len(mtspsolution)#其实就是初始种群数，我这里写的有些繁琐了
     pass
 #目标函数1：计算解的路程成本
    def distance_cost(self,distmatrix,judge):#这个judge是用来控制输出的
         distcost=np.zeros([self.numsolution,self.numsalesman])#储存每个解中每个震源车所行路程
         distcost_everysolution=np.zeros([self.numsolution,1])#储存每个解的总路程
         for i, sol in enumerate(self.solution):
            for j, carsolution in enumerate(sol):
                dist=0
                if len(carsolution) > 1:
                    dist = sum(distmatrix[carsolution[k]][carsolution[k + 1]] for k in range(len(carsolution) - 1))
                distcost[i, j] = dist
                distcost_everysolution[i] += dist
               
                  
         #根据需要返回每个震源车所行路程或整条路线路程
         if judge=='distcost':#这个是返回一个解中每个震源车所行路程
          return distcost
         elif judge=='disteverysolution':#返回一个解的总路程
          return distcost_everysolution
         else:
            raise ValueError("Invalid value for 'judge'. Please specify 'distcost' or 'disteverysolution'.")
 #目标函数2：时间成本
    def time_balance(self,distmatrix,everyworktime,velocity,judge):
        #everyworktime是震源车在每个炮点的工作时间，假设是固定的
        #velocity是震源车前进速度，假设是固定的
        timecost=np.zeros([self.numsolution,1])#用来储存每个解的时间成本
        for i in range(self.numsolution):
             TD=TDtotaltime()
             second,completecartime=TD.td_totaltime(self.solution[i], everyworktime, velocity, distmatrix)
             #second是一个解的时间成本
             #complcartime是一个解中每个震源车的时间成本
             timecost[i]=second
        if judge== 'distcost':   #judge也是用于控制输出的，后续要用到 
          return completecartime
        elif judge=='disteverysolution':
          return timecost
        
    def totalcost(self,distmatrix,everyworktime,velocity,judge):#把路程和时间成本组成一个列表返回
        distcost=self.distance_cost(distmatrix,judge)
        timecost=self.time_balance(distmatrix, everyworktime, velocity,judge)
        
        return [distcost,timecost]

#示例：
# positions=np.load('position.npy')#这个是随机生成的一组坐标，也在压缩包里面
# Data=Dataprocess(positions)
# ini=Initialpopcreat()
# G=Data.create_graph()
# solution=ini.initialpopulation(G,8,6)
# distmatrix=Data.build_dist_mat()
# solution1=[[[3, 15, 14, 16, 11, 18],[13, 17, 8, 6],[10, 5, 2, 0],[9, 7, 12, 4, 1, 19]]]
# worktime=6
# v=20
# distmatrix=Data.build_dist_mat()
# Cost=Evaluator_solution(solution1,  len(solution1))
# discost=Cost.distance_cost(distmatrix,'disteverysolution')
# std_array=Cost.time_balance(distmatrix, 6, 20)       
# total=Cost.totalcost(distmatrix, 6, 20,'disteverysolution')
