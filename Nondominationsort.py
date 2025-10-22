import numpy as np
import copy
#非支配排序以及拥挤度计算
class Non_domination_sort:
    def __init__(self, solution,totalcost):
        self.solution = solution
        self.totalcost=totalcost
        pass
 
    #非支配排序
    def non_domination_sort(self):
        F1 = []  # 储存第一非支配前沿
        F = []  # 储存所有前沿
        s = []  # 储存解所支配的解
        n = [] # 储存解被支配的次数
        sortsolution=[None]*len(self.solution)#用于记录每个解所在的前沿序号
        N = len(self.solution)
        for i in range(N):
            si = []  # 用于储存解i支配的解
            ni = 0  # 用于记录i被支配的解个数
            for j in range(N):
                dom_less = 0
                dom_equal = 0
                dom_more = 0
                for k in range(len(self.totalcost)):  # 判断个体i和个体j的支配关系
                    if self.totalcost[k][i] < self.totalcost[k][j]:
                        dom_less += 1
                    elif self.totalcost[k][i] == self.totalcost[k][j]:
                        dom_equal += 1
                    else:
                        dom_more += 1
                if dom_less == 0 and dom_equal != len(self.totalcost):  # 说明i受j支配,相应的n加1
                    ni += 1
                elif dom_more == 0 and dom_equal != len(self.totalcost):  # 说明i支配j,把j加入i的支配合集中
                    si.append(j)
            n.append(ni)
            if ni == 0:
                F1.append(i)
                sortsolution[i]=1
            s.append(si)

        F.append(F1)  # 第一非支配前沿找到
        #寻找剩余支配前沿
        i = 0
        while len(F[i]) != 0:
            Q = []
            for p in F[i]:
                for q in s[p]:
                    n[q] = n[q] - 1
                    if n[q] == 0:
                        Q.append(q)
                        sortsolution[q]=i+2
            F.append(Q)
            i = i + 1
        return F,sortsolution#返回每个解的前沿等级，不改变解得顺序
   # 拥挤度计算
    def crowding_distance(self,judge):
         objective=[]
         sorted_indices=[]
         num_solution=len(self.solution)
         crowding_distance =np.zeros(num_solution)
         for i in range(len(self.totalcost)):
             objectivei=self.totalcost[i]
             if judge==1:
                 flat_list = [item for sublist in objectivei for item in sublist]
                 sorted_indicesi =np.argsort(flat_list )
                 objective.append(objectivei)#用于目标函数
                 sorted_indices.append(sorted_indicesi)#储存根据目标函数排序解后的解原索引值
                 crowding_distance[sorted_indices[i][0]]=np.inf
                 crowding_distance[sorted_indices[i][-1]] = np.inf
             elif judge==2:
                 # flat_list = [item for sublist in objectivei for item in sublist]
                 sorted_indicesi =np.argsort(objectivei)
                 objective.append(objectivei)#用于目标函数
                 sorted_indices.append(sorted_indicesi)#储存根据目标函数排序解后的解原索引值
                 crowding_distance[sorted_indices[i][0]]=np.inf
                 crowding_distance[sorted_indices[i][-1]] = np.inf  
         for j in range(1, num_solution-1):
              for k in range(len(self.totalcost)):
                crowding_distance[sorted_indices[k][j]] += (objective[k][sorted_indices[k][j + 1]] - objective[k][sorted_indices[k][j - 1]]) / (objective[k].max() - objective[k].min())
         return crowding_distance#返回每个解的拥挤度，不改变解的索引顺序

#用法示例：                
# positions=np.load('position.npy')
# Data=Dataprocess(positions)
# ini=Initialpopcreat()
# G=Data.create_graph()
# solution=ini.initialpopulation(G,8,6)
# distmatrix=Data.build_dist_mat()
# solution1=[[[3, 15, 14, 16, 11, 18],[13, 17, 8, 6],[10, 5, 2, 0],[9, 7, 12, 4, 1, 19]]]
# worktime=6
# v=20
# distmatrix=Data.build_dist_mat()
# Cost=Evaluator_solution(solution, len(solution))    
# total=Cost.totalcost(distmatrix, 6, 20,'disteverysolution')
# Sort = Non_domination_sort(solution,total)
# F,S= Sort.non_domination_sort()
# c=Sort.crowding_distance()

            
            
        
        
        