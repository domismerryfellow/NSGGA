import numpy as np
import math
import copy
import tqdm
class T:
    def __init__(self):
        pass
    def Tcreate_array(self, mtsp, worktime, v, distmatrix):
        T = []
        for route in mtsp:
            numrows = len(route)
            numcolumns = 1000000
            array = np.zeros((numrows, numcolumns), dtype=int)
            T.append(array)
        
        for i in range(len(T)):
            A0 = T[i][0]
            A0[1:worktime+1] = 1
            x = worktime
            movetime = 0 if len(mtsp[i]) == 1 else math.ceil(distmatrix[mtsp[i][0], mtsp[i][1]] / v)
            T[i][0] = A0

            for j in range(1, len(T[i])):
                Aj = T[i][j]
                Aj[x+movetime+1:x+movetime+worktime+1] = 1
                T[i][j] = Aj
                x += movetime + worktime
                movetime = math.ceil(distmatrix[mtsp[i][j], mtsp[i][j + 1]] / v) if j != len(T[i]) - 1 else 0
        return T

    def conditionjudge(self, second, Tlist, mtsp):
        movecar = []
        readycarindex = []
        readycarlocation = []
        workcarindex = []
        workcarlocation = []
        stopcarindex = []
        stopcarlocation = []

        for i in range(len(Tlist)):
            subT = Tlist[i]
            Ai = subT[:, second]
            Aj = subT[:, second + 1]
            time = [0, 0]
            location = -1
            
            for n, j in enumerate(Ai):
                if j == 1:
                    time[0] = 1
                    location = n
                    break
            
            for nn, k in enumerate(Aj):
                if k == 1:
                    time[1] = 1
                    location = nn
                    break
            
            if time == [0, 0]:
                movecar.append(i)
            elif time == [0, 1]:
                readycarindex.append(i)
                readycarlocation.append(mtsp[i][location])
            elif time == [1, 1]:
                workcarindex.append(i)
                workcarlocation.append(mtsp[i][location])
            else:
                stopcarindex.append(i)
                stopcarlocation.append(mtsp[i][location])
        
        readycar = [readycarindex, readycarlocation]
        workcar = [workcarindex, workcarlocation]
        stopcar = [stopcarindex, stopcarlocation]

        return movecar, readycar, workcar, stopcar

    def completejudge(self, second, T, stopcar, mtsp):
        stopnum = 0
        stopcarfin = []
        for i in range(len(stopcar[0])):
            num = len(mtsp[stopcar[0][i]])
            if stopcar[1][i] == mtsp[stopcar[0][i]][num - 1]:
                stopnum += 1
                stopcarfin.append(stopcar[0][i])
        return stopnum, stopcarfin

    def situation2_nowork_readyover1(self, second, T, mtsp, readycar, workcar):
        car = []
        carwork = []

        for i in range(len(readycar[0])):
            cari = mtsp[readycar[0][i]]
            car.append(readycar[0][i])
            for j, location in enumerate(cari):
                if location == readycar[1][i]:
                    carwork.append(j)
                    break

        min_work = min(carwork)
        min_work_cars = [car[j] for j, work in enumerate(carwork) if work == min_work]
        selected_car = np.random.choice(min_work_cars)

        
        readycar[1].remove(readycar[1][readycar[0].index(selected_car)])
        readycar[0].remove(selected_car)
        for i in readycar[0]:
            newcolumn = np.zeros(len(T[i]))
            T[i] = np.insert(T[i], second + 1, newcolumn, axis=1)

        return T

    def time_distance(self, x):
        if 0 < x <= 500:
            return 7
        elif 500 < x <= 750:
            return 24 - (7 / 250) * x
        else:
            return 0

    def alreadyworktime(self, T, second, workcari):
        A = T[workcari]
        worktime = 0
        for column in range(second - 1, -1, -1):
            if np.all(A[:, column] == 0):
                break
            worktime += np.sum(A[:, column])
        return worktime 

    def situation3_workcarover0_readycarover1(self, second, T, mtsp, readycar, workcar, distmatrix):
        waitcar = []
        unwaitcar = [[], []]
        
        for i in range(len(readycar[0])):
            waittime = []
            nowi = readycar[1][i]

            for j in range(len(workcar[0])):
                nowj = workcar[1][j]
                dis = distmatrix[nowi][nowj]
                huadongtime = self.time_distance(dis)

                if huadongtime != 0:
                    worktimej = self.alreadyworktime(T, second, workcar[0][j])
                    realwaittimei = huadongtime - worktimej
                    waittime.append(realwaittimei)
                else:
                    waittime.append(0)

            if any(waittime):
                waitcar.append(readycar[0][i])
            else:
                unwaitcar[0].append(readycar[0][i])
                unwaitcar[1].append(readycar[1][i])

        for car in waitcar:
            newcolumn = np.zeros(len(T[car]))
            T[car] = np.insert(T[car], second + 1, newcolumn, axis=1)

        if len(unwaitcar[0]) > 1:
            car = []
            carwork = []
            for i in range(len(unwaitcar[0])):
                cari = mtsp[unwaitcar[0][i]]
                car.append(unwaitcar[0][i])
                for j, location in enumerate(cari):
                    if location == unwaitcar[1][i]:
                        carwork.append(j)
                        break

            min_work = min(carwork)
            min_work_cars = [car[j] for j, work in enumerate(carwork) if work == min_work]
            selected_car = np.random.choice(min_work_cars)
            unwaitcar[1].remove(unwaitcar[1][unwaitcar[0].index(selected_car)])
            unwaitcar[0].remove(selected_car)
            for i in unwaitcar[0]:
                newcolumn = np.zeros(len(T[i]))
                T[i] = np.insert(T[i], second + 1, newcolumn, axis=1)

        return T

    def td_totaltime(self, mtspsolution, worktime, v, distmatrix):
        T = self.Tcreate_array(mtspsolution, worktime, v, distmatrix)
        
        numcompletecar = 0
        completecartime = [None] * len(T)
        
        for second in range(100000):
            movecar, readycar, workcar, stopcar = self.conditionjudge(second, T, mtspsolution)
            complete, car = self.completejudge(second, T, stopcar, mtspsolution)
            numcompletecar += complete

            if numcompletecar > 0:
                for c in car:
                    completecartime[c] = second

            if numcompletecar == len(T):
                break

            if len(readycar[0]) == 0 or (len(readycar[0]) == 1 and len(workcar[0]) == 0):
                continue
            elif len(readycar[0]) > 1 and len(workcar[0]) == 0:
                T = self.situation2_nowork_readyover1(second, T, mtspsolution, readycar, workcar)
            elif len(readycar[0]) >= 1 and len(workcar[0]) != 0:
                T = self.situation3_workcarover0_readycarover1(second, T, mtspsolution, readycar, workcar, distmatrix)

        return T
        
class TDtotaltime:
    def __init__(self):
        pass
    # 对每个MTSP解，对其中每个震源车构建不加滑动时间的炮点激发状态表T
    # 首先构建空表T，行为炮点，列为时间（第i秒）,T构建为数组形式
    # 1.初始化状态表
    def Tcreate_array(self, mtsp, worktime, v, distmatrix):
        #动态扩展T的大小
        T = []
        for route in mtsp:
            numrow = len(route)
            initial_columns = 100  #可扩展
            array = np.zeros((numrow, initial_columns), dtype=int)
            T.append(array)
        #根据工作时间和移动时间把表格初始化为不加waittime的状态
        #0为move，1为work
        #移动时间直接用的dis/v
        #把1填进去
        for i, route in enumerate(mtsp):
            x = worktime
            if len(route) > 1:
                movetime = math.ceil(distmatrix[route[0], route[1]] / v)
            else:
                movetime = 0
            T[i][0, 1:worktime+1] = 1#先处理第0个震源车的表，为了产生movetime用于处理后续的
           
            for j in range(1, len(route)):
                if x + movetime + worktime >= T[i].shape[1]:#首先判断震源车活动时间是否超过表限制，如果是先扩展表后填数
                    T[i] = np.pad(T[i], ((0, 0), (0, x + movetime + worktime - T[i].shape[1] + 100)), 'constant')
                    
                    #在原本Ti的基础上扩展列，列数为活动时间减去现有列数再加100
                T[i][j, x+movetime+1:x+movetime+worktime+1] = 1
                x += movetime + worktime
                if j != len(route) - 1:
                    movetime = math.ceil(distmatrix[route[j], route[j+1]] / v)#移动时间可能不为整数，向上取整
                else:
                    movetime = 0
        return T

    #2.判断a秒震源车状态以及a秒震源车所处炮点位置
    #movecar无法判断点位，炮点位置不处理movecar
    def conditionjudge(self, second, Tlist, mtsp):
        #遍历a列和a+1列
        #00-movecar
        #01-readycar
        #11-workcar
        #10-stopcar
        movecar=[]
        #储存移动中的车
        readycarindex=[]
        readycarlocation=[]
        #储存准备状态的车以及该车目前所在炮点位置
        workcarindex=[]
        workcarlocation=[]
        #储存工作状态的车以及该车目前所在炮点位置
        stopcarindex=[]
        stopcarlocation=[]
        #储存准备停止状态的车以及该车目前所在炮点位置
        for i, subT in enumerate(Tlist):
            if second >= subT.shape[1]:  
                continue
            if second + 1 >= subT.shape[1]:
                #判断second是否在原状态表时间范围内，如果不在需要进行扩展
                subT = np.pad(subT, ((0, 0), (0, 10)), 'constant')
                Tlist[i] = subT
            Ai = subT[:, second]
            Aj = subT[:, second + 1]
            time = [0, 0]
            
            location = -1
            for n, j in enumerate(Ai):
                if j == 1:
                    time[0] = 1
                    location = n

            for nn, k in enumerate(Aj):
                if k == 1:
                    time[1] = 1
                    location = nn#震源车正在他路线上的第nn个炮点工作

            if time == [0, 0]:
                movecar.append(i)
            elif time == [0, 1]:
                readycarindex.append(i)
                readycarlocation.append(mtsp[i][location])
            elif time == [1, 1]:
                workcarindex.append(i)
                workcarlocation.append(mtsp[i][location])
            else:
                stopcarindex.append(i)
                stopcarlocation.append(mtsp[i][location])

        readycar = [readycarindex, readycarlocation]
        workcar = [workcarindex, workcarlocation]
        stopcar = [stopcarindex, stopcarlocation]

        return movecar, readycar, workcar, stopcar

   #3.停止条件
   #判断每个震源车是否停止工作：在每一秒判断stopcar中是否有车i
   #如果有判断i所在炮点是不是i车路线终点，若是则i停止，停止工作的车辆数num+1

    def completejudge(self, second, T, stopcar, mtsp):
        stopnum = 0
        stopcarfin = []

        for i in range(len(stopcar[0])):
            num = len(mtsp[stopcar[0][i]])
            if stopcar[1][i] == mtsp[stopcar[0][i]][num - 1]:
                stopnum += 1
                stopcarfin.append(stopcar[0][i])

        return stopnum, stopcarfin
    #Q1:如何判断总工作停止？
    #A1:num是否等于numsalesman，是则输出时间a       
    #情况1
    #不存在readycar或者只有一个readycar不存在workcar：无需计算滑动时间，没有车要等待，T不变
    #情况2
    #readycar>1,workcar=0
    #此时需要选一个目前工作量最小的车，此车work，其余车继续ready，T表其余车这行在此秒列加0，后移其余元素
    def situation2_nowork_readyover1(self, second, T, mtsp, readycar, workcar):
        carwork = [next(i for i, location in enumerate(mtsp[cari]) if location == readycar[1][j]) 
                   for j, cari in enumerate(readycar[0])]
        min_work = min(carwork)
        min_work_cars = [readycar[0][j] for j, work in enumerate(carwork) if work == min_work]
        selected_car = np.random.choice(min_work_cars)
        readycar[0].remove(selected_car)
        readycar[1].remove(mtsp[selected_car][min_work])

        for i in readycar[0]:
            newcolumn = np.zeros(len(T[i]))
            T[i] = np.insert(T[i], second + 1, newcolumn, axis=1)

        return T

    def time_distance(self, x):
        if 0 < x <= 500:
            return 7
        elif 500 < x <= 750:
            return 24 - (7 / 250) * x
        else:
            return 0

    def alreadyworktime(self, T, second, workcari):
        A = T[workcari]
        worktime = 0
        for column in range(second - 1, -1, -1):
            if np.all(A[:, column] == 0):
                break
            worktime += np.sum(A[:, column])
        return worktime

    def situation3_workcarover0_readycarover1(self, second, T, mtsp, readycar, workcar, distmatrix):
        waitcar = []
        unwaitcar = [[], []]

        for i, car in enumerate(readycar[0]):
            nowi = readycar[1][i]
            waittime = [
                self.time_distance(distmatrix[nowi][workloc]) - self.alreadyworktime(T, second, workcar[0][j])
                for j, workloc in enumerate(workcar[1])
            ]

            if any(wait > 0 for wait in waittime):
                waitcar.append(car)
            else:
                unwaitcar[0].append(car)
                unwaitcar[1].append(nowi)

        for car in waitcar:
            newcolumn = np.zeros(len(T[car]))
            T[car] = np.insert(T[car], second + 1, newcolumn, axis=1)

        if len(unwaitcar[0]) > 1:
            carwork = [next(i for i, location in enumerate(mtsp[cari]) if location == unwaitcar[1][j]) 
                       for j, cari in enumerate(unwaitcar[0])]
            min_work = min(carwork)
            min_work_cars = [unwaitcar[0][j] for j, work in enumerate(carwork) if work == min_work]
            selected_car = np.random.choice(min_work_cars)

            unwaitcar[0].remove(selected_car)
            unwaitcar[1].remove(mtsp[selected_car][min_work])

            for i in unwaitcar[0]:
                newcolumn = np.zeros(len(T[i]))
                T[i] = np.insert(T[i], second + 1, newcolumn, axis=1)

        return T

    def td_totaltime(self, mtspsolution, worktime, v, distmatrix):
        T = self.Tcreate_array(mtspsolution, worktime, v, distmatrix)
        numcompletecar = 0
        completecartime = [None] * len(T)
        for second in range(100000):
            movecar, readycar, workcar, stopcar = self.conditionjudge(second, T, mtspsolution)
            complete, car = self.completejudge(second, T, stopcar, mtspsolution)
            numcompletecar += complete
            if numcompletecar != 0:
                for i in range(len(car)):
                    completecartime[car[i]] = second
            if numcompletecar == len(T):
                break
            
            if not readycar[0]:
                continue
            elif len(readycar[0]) > 1 and not workcar[0]:
                T = self.situation2_nowork_readyover1(second, T, mtspsolution, readycar, workcar)
            elif readycar[0] and workcar[0]:
                T = self.situation3_workcarover0_readycarover1(second, T, mtspsolution, readycar, workcar, distmatrix)
        
        return   second+1,completecartime




    




         
