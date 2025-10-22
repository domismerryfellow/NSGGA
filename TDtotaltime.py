import numpy as np
import math
import copy
import tqdm

#TD规则下的工作时间仿真模型

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
class TDtotaltimeold:
    def __init__(self):
        pass
    
    #对每个MTSP解，对其中每个震源车构建不加滑动时间的炮点激发状态表T
    #首先构建空表T，行为炮点，列为时间（第i秒）,T构建为数组形式
    #1.初始化状态表
    def Tcreate_array(self,mtsp,worktime,v,distmatrix):#输入[[],[],[]]形式的解
        #针对此解的每个震源车创建T表
        T=[]
        for routei in mtsp:
          numrow=len(routei)#行数
          numcolumns=1000000#列数
          array =np.zeros((numrow, numcolumns), dtype=int)  
          T.append(array)
        #根据工作时间和移动时间把表格初始化为不加waittime的状态
        #0为move，1为work
        #移动时间直接用的dis/v
        #把1填进去
        for i in range(len(T)):
          #先处理第0个震源车的表，为了产生movetime用于处理后续的
          A0=T[i][0]
          A0[1:worktime+1]=1
          x=worktime
          if len(mtsp[i])==1:
              movetime=0
          else:
              movetime=math.ceil((distmatrix[mtsp[i][0],mtsp[i][1]])/v)
          T[i][0]=A0
    
        #分布处理后续所有震源车的表
          for j in range(1,(len(T[i]))):
            Aj=T[i][j]
            Aj[x+movetime+1:x+movetime+worktime+1]=1
            T[i][j]=Aj
            x=x+movetime+worktime
            if j!=len(T[i])-1:
              movetime=math.ceil((distmatrix[mtsp[i][j],mtsp[i][j+1]])/v)#移动时间可能不是整数所以这里向上取整了
            else: 
              movetime=0
        return T



    #2.判断a秒震源车状态以及a秒震源车所处炮点位置
    #movecar无法判断点位，炮点位置不处理movecar
    def conditionjudge(self,second,Tlist,mtsp):
        #遍历a列和a+1列
        #00-movecar
        #01-readycar
        #11-workcar
        #10-stopcar
        a=second #没必要的一个处理
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
        for i in range(len(Tlist)):
            subT=Tlist[i]
            Ai=subT[:,a]#把车i的第a列提出来
            Aj=subT[:,a+1]#把车i的第a+1列提出来
            time=[0]*2#用于后续判断状态
            n=0#用于后续判断所在位置
            for j in Ai:
                #遍历a列
                if j ==1:
                    time[0]=1
                    location=n
                n=n+1
                
            nn=0
            for k in Aj:
                #遍历a+1列
                if k ==1:
                    time[1]=1
                    location=nn#震源车正在他路线上的第nn个炮点工作
                nn=nn+1
            
            if time==[0,0]:
                movecar.append(i)
            elif time==[0,1]:
                readycarindex.append(i)
                readycarlocation.append(mtsp[i][location]) 
            elif time==[1,1]:
                workcarindex.append(i)
                workcarlocation.append(mtsp[i][location])
            else:
                stopcarindex.append(i)
                stopcarlocation.append(mtsp[i][location])
        readycar=[readycarindex,readycarlocation]
        workcar=[workcarindex,workcarlocation]
        stopcar=[stopcarindex,stopcarlocation]
        
        return movecar,readycar,workcar,stopcar


    #3.停止条件
    #判断每个震源车是否停止工作：在每一秒判断stopcar中是否有车i
    #如果有判断i所在炮点是不是i车路线终点，若是则i停止，停止工作的车辆数num+1

    def completejudge(self,second,T,stopcar,mtsp):
        
        stopnum=0#判断震源车停止没有
        stopcarfin=[]#储存停止工作的震源车
        for i in range(len(stopcar[0])):
            num=len(mtsp[stopcar[0][i]])
            
            if stopcar[1][i]==mtsp[stopcar[0][i]][num-1]:
                stopnum+=1
                stopcarfin.append(stopcar[0][i])
        return stopnum,stopcarfin


    #Q1:如何判断总工作停止？
    #A1:num是否等于numsalesman，是则输出时间a       

    #情况1
    #不存在readycar或者只有一个readycar不存在workcar：无需计算滑动时间，没有车要等待，T不变

    #情况2
    #readycar>1,workcar=0
    #此时需要选一个目前工作量最小的车，此车work，其余车继续ready，T表其余车这行在此秒列加0，后移其余元素
    def situation2_nowork_readyover1(self,second,T,mtsp,readycar,workcar):
        #计算readycar工作量
        car=[]
        carwork=[]
        for i in range(len(readycar[0])):#遍历处于准备状态的车
            cari=mtsp[readycar[0][i]] #储存准备状态车i的路线
            car.append(readycar[0][i])#把准备状态的车提出来，这里其实想做一个列表，列表[0]表示车号，[1]表示车路线，把他们组装起来
            for j in range(len(cari)):#但是不组装也可以
                if cari[j]==readycar[1][i]:
                    carwork.append(j)
                    break #这里就是算每个车已经走过多少炮点
        winner=[]
        winnerlong=min(carwork)
        for j in range(len(car)):
            if carwork[j]==winnerlong:
                winner.append(car[j])
        #选出工作量最小的，因为工作量最小的车可能不为1
        #如果不为1，随机选一个
        if len(winner)>1:
            rd=np.random.randint(0,len(winner))
        else:
            rd=0
        #winner[rd]车T不变，其余车等待
        index=readycar[0].index(winner[rd])
        readycar[0].remove(winner[rd])
        #可以继续工作的car-winner[rd]
        readycar[1].remove(readycar[1][index])
        Tcopy=T.copy()#把T拷贝一下
        for i in readycar[0]:
            newcolumn=np.zeros(len(Tcopy[i]))
            column_index = second  # 插入到第二列之后
            Tcopy[i]= np.insert(Tcopy[i], column_index + 1, newcolumn, axis=1)
        return Tcopy

    #情况3.readycar>=1,workcar>0,需要根据TD规则计算滑动时间
    #TD规则
    def time_distance(self, x):
        if 0 < x <= 500:
            return 7
        elif 500 < x <= 750:
            return 24 - (7 / 250) * x
        else:
            return 0
        
    #计算工作车已经工作时间
    def alreadyworktime(self,T,second,workcari):
        #从second这一列开始往前遍历列，直到一列全为0
        A=T[workcari]
        worktime=0
        for columnum in range(second-1, -1, -1):
            column=A[:,columnum]
            j=0
            for i in column:
                
                if i==1:
                    worktime=worktime+1
                elif i==0:
                    j+=1
            if j==len(column):
              break
        return worktime 


    def situation3_workcarover0_readycarover1(self,second,T,mtsp,readycar,workcar,distmatrix):
        waitcar=[]
        unwaitcar=[]
        unwaitcar0=[]
        unwaitcar1=[]
        for i in range(len(readycar[0])):
            waittime=[]
            nowi=readycar[1][i]#准备车现在位置
            for j in range(len(workcar[0])):
                nowj=workcar[1][j]#工作车现在位置
                dis=distmatrix[nowi][nowj]#距离判断
                huadongtime=self.time_distance(dis)#理论滑动时间
                if huadongtime!=0:
                    worktimej=self.alreadyworktime(T,second,workcar[0][j])
                    realwaittimei=huadongtime-worktimej#实际等待时间等于理论滑动减去工作车已经工作时间
                    waittime.append(realwaittimei)
                else:
                    waittime.append(0)#储存的是震源车i在每个工作车影响下的所需等待时间
            n=0
            for k in waittime:
                n+=1
                if k !=0:#如果有一个等待时间不为0，说明此车需要等待，跳出循环，遍历下一个车
                    waitcar.append(readycar[0][i])
                    break
                elif k==0 and n==len(waittime):
                    unwaitcar0.append(readycar[0][i])
                    unwaitcar1.append(readycar[1][i])
            unwaitcar=[unwaitcar0,unwaitcar1]
        Tcopy=T.copy()            
        for car in waitcar:
            newcolumn=np.zeros(len(Tcopy[car]))#0列
            column_index = second  # 插入到第second列后
            Tcopy[car]= np.insert(Tcopy[car], column_index + 1, newcolumn, axis=1)
            
        if len(unwaitcar[0])>1:
            car=[]
            carwork=[]
            for i in range(len(unwaitcar[0])):#遍历处于准备状态的车
                cari=mtsp[unwaitcar[0][i]] #储存准备状态车i的路线
                car.append(unwaitcar[0][i])#把准备状态的车提出来，这里其实想做一个列表，列表[0]表示车号，[1]表示车路线，把他们组装起来
                for j in range(len(cari)):#但是不组装也可以
                    if cari[j]==unwaitcar[1][i]:
                        carwork.append(j)
                        break #这里就是算每个车已经走过多少炮点
            winner=[]
            winnerlong=min(carwork)
            for j in range(len(car)):
                if carwork[j]==winnerlong:
                    winner.append(car[j])
            #选出工作量最小的，因为工作量最小的车可能不为1
            #如果不为1，随机选一个
            if len(winner)>1:
                rd=np.random.randint(0,len(winner))
            else:
                rd=0
            #winner[rd]车T不变，其余车等待
            index=unwaitcar[0].index(winner[rd])
            unwaitcar[0].remove(winner[rd])
            #可以继续工作的car-winner[rd]
            unwaitcar[1].remove(unwaitcar[1][index])
            for i in unwaitcar[0]:
                newcolumn=np.zeros(len(Tcopy[i]))
                column_index = second  # 插入到第二列之后
                Tcopy[i]= np.insert(Tcopy[i], column_index + 1, newcolumn, axis=1)
        return Tcopy
              
    #主函数
    def td_totaltime(self,mtspsolution,worktime,v,distmatrix):
        T=self.Tcreate_array(mtspsolution,worktime,v,distmatrix)
        Tcopy=T
        numcompletecar=0#停止工作的车个数
        completecartime=[None]*len(T)#分别储存停止工作的车的总工作时间
        for second in range(100000):
            movecar,readycar,workcar,stopcar=self.conditionjudge(second,Tcopy,mtspsolution)
            complete,car=self.completejudge(second,Tcopy,stopcar,mtspsolution)
            numcompletecar+=complete
            #判断所有车是否停止工作，停止直接停止循环，返回时间
            if numcompletecar!=0:
              for i in range(len(car)):
                completecartime[car[i]]=second
            if numcompletecar==len(Tcopy):
                break
            #情况1
            elif len(readycar[0])==0 or (len(readycar[0])==1 and len(workcar[0])==0):
                continue
            #情况2
            elif len(readycar[0])>1 and len(workcar[0])==0:
                Tcopy=self.situation2_nowork_readyover1(second, Tcopy, mtspsolution, readycar, workcar)           
            #情况3
            elif len(readycar[0])>=1 and len(workcar[0])!=0:
                Tcopy=self.situation3_workcarover0_readycarover1(second, Tcopy, mtspsolution, readycar, workcar,distmatrix)
        second+=1
        return Tcopy




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
    # def time_distance(self, x):
    #     if 0 < x <= 500:
    #         return 7
    #     elif 500 < x <= 750:
    #         return 24 - (7 / 250) * x
    #     else:
    #         return 0
    # def time_distance(self,x):
    #     y=0
    #     if x<=2500 and x>0:
    #         y=20
    #     elif x>2500 and x<=10000:
    #         y=(80/3)-(1/375)*x
    #     elif x>10000:
    #         y=0
    #     return y
    
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




    
if __name__ == '__main__':
    #测试代码：
    from Datacreat import Dataprocess
    from new import population
    import pandas as pd
    import matplotlib.pyplot as plt
    
    path = r'data\example101.csv'
    data=pd.read_csv(path,usecols=['Vibrator', 'ActualX','ActualY'])#读取震源车以及炮点坐标列
    first_x_rows = data.head(1000)#这里是用了第一个csv的前100个数据，因为内存原因处理不了1w个
    unique_values = first_x_rows['Vibrator'].drop_duplicates()
    a = []
    for i in unique_values:
        specified_rows_index = first_x_rows[first_x_rows['Vibrator'] == i].index
        a.append(list(specified_rows_index))
    solu = []
    solu.append(a)
    solution1=solu[0]
    solution1=[[231, 234, 236, 239, 242, 243, 246, 249, 252, 255, 257, 259, 260, 263, 265, 267, 269, 271, 274, 277, 279, 282, 285, 287, 290, 293, 296, 298, 301, 303, 306, 309, 313, 317, 320, 272, 300, 304, 341, 337, 307, 311, 315, 297, 294, 318, 322, 289, 291, 284, 281, 278, 275, 270, 268, 258, 261, 266, 264, 262, 251, 254, 256, 245, 248, 240, 237, 230, 233, 226, 228, 222, 223, 224, 221, 220, 219, 218, 216, 343, 346, 348, 352, 354, 340, 335, 210, 213, 204, 202, 200, 207, 75, 73, 71, 68, 64, 61, 58, 105, 103, 109, 107, 124, 111, 101, 99, 55, 52, 77, 79, 81, 82, 49, 46, 43, 40, 84, 86, 88, 92, 89, 94, 31, 34, 37, 114, 118, 121, 128, 131, 133, 171, 137, 140, 154, 59, 56, 53, 50, 47, 45, 42, 39, 36, 32, 29, 27, 145, 148, 184, 253, 250, 247, 244, 241, 238, 235, 232, 229, 227, 225, 526, 530, 533, 606, 608, 583, 586, 588, 612, 614, 615, 616, 591, 603, 594, 597, 599, 545, 543, 540, 537, 576, 573, 570, 567, 564, 561, 559, 578, 557, 554, 551, 548, 194, 193, 190, 188, 185, 182, 180, 178, 175, 173, 170, 168, 167, 166, 165, 164, 163, 162, 160, 158, 156, 153, 151, 149, 146, 143, 141, 138, 135, 132, 129, 126, 123, 120, 117, 115, 112, 161, 159, 157, 155, 152, 150, 147, 144, 142, 139, 136, 134, 130, 127, 125, 122, 119, 116, 113, 110, 108, 106, 104, 102, 100, 98, 97, 96, 95, 93, 91, 90, 87, 85, 83, 80, 78, 76, 74, 72, 70, 67, 65, 62, 358, 361, 365, 367, 370, 371, 374, 377, 380, 382, 385, 387, 390, 393, 217, 215, 214, 212, 211, 209, 208, 206, 205, 203, 201, 199, 198, 197, 196, 195, 192, 191, 189, 187, 186, 183, 181, 179, 177, 176, 174, 172, 169]
,
[613, 611, 610, 607, 604, 601, 598, 595, 592, 589, 585, 584, 581, 579, 575, 571, 568, 565, 562, 558, 555, 553, 550, 546, 542, 538, 534, 529, 525, 521, 519, 515, 511, 508, 505, 501, 498, 916, 923, 917, 924, 922, 925, 926, 927, 928, 931, 932, 964, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 930, 929, 920, 921, 919, 912, 918, 913, 911, 910, 914, 915, 909, 908, 907, 906, 905, 904, 903, 902, 901, 899, 875, 874, 873, 872, 871, 870, 869, 868, 867, 866, 860, 865, 862, 857, 855, 853, 839, 841, 844, 836, 834, 833, 820, 823, 817, 815, 825, 827, 830, 846, 848, 851, 864, 863, 710, 707, 702, 699, 694, 691, 687, 684, 679, 676, 671, 667, 664, 662, 658, 655, 653, 651, 649, 647, 645, 641, 785, 788, 790, 792, 794, 797, 799, 801, 804, 806, 808, 725, 720, 811, 813, 965, 966, 967, 968, 969, 970, 971, 973, 972, 974, 975, 976, 977, 980, 981, 982, 983, 984, 995, 996, 997, 998, 999, 994, 985, 986, 979, 978, 987, 988, 989, 990, 991, 992, 993]
,
[455, 451, 446, 442, 438, 434, 431, 427, 422, 418, 414, 411, 409, 407, 404, 403, 401, 399, 397, 395, 394, 391, 388, 384, 381, 378, 375, 372, 368, 362, 359, 355, 350, 345, 342, 338, 334, 331, 328, 325, 323, 319, 316, 312, 308, 305, 302, 299, 295, 292, 288, 286, 283, 280, 276, 273, 757, 755, 753, 751, 749, 747, 742, 744, 740, 739, 738, 736, 728, 730, 732, 734, 719, 722, 724, 726, 2, 1, 712, 700, 703, 705, 708, 669, 666, 663, 660, 657, 650, 652, 654, 646, 648, 623, 622, 621, 620, 619, 624, 625, 642, 644, 0, 673, 675, 678, 640, 639, 626, 627, 618, 617, 628, 630, 633, 635, 637, 681, 683, 686, 689, 697, 695, 692, 714, 716, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 30, 33, 35, 38, 41, 44, 48, 51, 54, 57, 60, 63, 66, 69]
,
[771, 770, 769, 643, 656, 659, 638, 636, 634, 632, 631, 665, 661, 772, 773, 774, 802, 803, 805, 807, 809, 810, 812, 814, 816, 818, 819, 821, 800, 796, 798, 795, 793, 778, 779, 791, 824, 822, 845, 847, 849, 850, 852, 854, 856, 843, 842, 826, 828, 829, 831, 840, 838, 837, 858, 859, 835, 861, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 895, 894, 893, 886, 887, 888, 889, 832, 890, 891, 892, 896, 897, 898, 900, 784, 786, 787, 789, 783, 782, 781, 780, 677, 674, 672, 777, 776, 775, 670, 668, 629, 709, 706, 704, 715, 717, 718, 721, 696, 698, 701, 680, 682, 685, 688, 690, 693, 723, 516, 514, 495, 494, 492, 486, 484, 475, 470, 467, 479, 482, 488, 490, 497, 512, 500, 509, 506, 503, 522, 524, 528, 532, 536, 539, 582, 580, 577, 541, 544, 547, 574, 587, 590, 572, 549, 556, 552, 569, 566, 563, 560, 596, 593, 600, 602, 605, 609, 413, 416, 420, 423, 425, 428, 430, 433, 437, 441, 445, 448, 452, 454, 458, 459, 462, 464, 466, 469, 471, 473, 476, 478, 456, 453, 460, 463, 449, 444, 440, 436, 432, 429, 480, 426, 421, 419, 415, 410, 412, 408, 406, 347, 351, 353, 356, 360, 333, 330, 329, 326, 363, 366, 741, 743, 727, 731, 729, 733, 735, 713, 711, 737, 745, 746, 748, 768, 535, 531, 483, 481, 477, 487, 485, 527, 523, 520, 767, 750, 752, 766, 765, 764, 754, 756, 758, 759, 760, 761, 762, 763, 518, 517, 513, 510, 507, 457, 461, 465, 504, 502, 493, 499, 491, 496, 489, 468, 472, 474, 435, 439, 443, 447, 450, 402, 400, 398, 396, 389, 405, 392, 386, 417, 383, 424, 379, 376, 373, 369, 364, 357, 349, 344, 339, 336, 332, 327, 324, 321, 314, 310]]
#     solution1=[[361, 511, 480, 15, 80, 712],
#                [342, 581, 903, 717, 906, 222, 282, 941],
#                [821, 486, 193, 636, 891, 956, 87, 69, 326, 601, 479, 235, 666, 146, 169, 397, 195, 495, 320, 343, 345, 200, 461, 128, 258, 453, 855, 325, 690, 143, 445, 760, 696, 785, 819, 659, 371, 927, 731, 883, 170, 998, 658, 774, 76, 637, 807, 590, 572, 370, 734, 684, 250, 763, 555, 970, 683, 865, 424, 963, 890, 101, 664, 521, 582, 422, 847, 74, 452, 300, 286, 728, 168, 310, 759, 743, 2, 134, 917, 966, 304, 376, 167, 707, 28, 536, 800, 988, 625, 595, 543, 419, 245, 749, 271, 550, 520, 372, 662, 697, 836, 12, 742, 81, 504, 272, 237, 385, 502, 358, 108, 36, 260, 95, 83, 384, 859, 568, 958, 71, 995, 907, 443, 751, 922, 468, 782, 902, 8, 292, 440, 405, 323, 254, 926, 276, 177, 197, 23, 991, 309, 804, 528, 933, 822, 723, 736, 0, 685, 198, 163, 290, 296, 312, 109, 375, 297, 783, 792, 955, 113, 627, 757, 85, 156, 523, 857, 444, 289, 103, 447, 99, 775, 870, 66, 866, 37, 977, 231, 318, 293, 207, 48, 551, 435, 493, 114, 423, 302, 596, 887, 861, 223, 645, 920, 129, 51, 298, 900, 569, 729, 417, 597, 472, 620, 740, 64, 13, 281, 537, 217, 141, 563, 513, 232, 412, 403, 812, 224, 795, 599, 705, 171, 14, 670, 467, 390, 614, 60, 383, 172, 661, 82, 968, 901, 454, 474, 407, 693, 615, 525, 562, 127, 482, 462, 106, 252, 180, 589, 945, 752, 779, 554, 960, 199, 784, 356, 576, 879, 414, 992, 629, 205, 888, 769, 161, 17, 78, 54, 494, 380, 638, 332, 145, 118, 11, 650, 680, 802, 869, 721, 97, 70, 110, 990, 4, 352, 56, 747, 348, 111, 137, 306, 386, 876, 49, 307, 643, 466, 136, 321, 858, 632, 86, 987, 221, 985, 455, 918, 899, 269, 936, 675, 813, 488, 880, 788, 579, 910, 116, 413, 295, 772, 805, 160, 484, 349, 897, 216, 515, 105, 695, 303, 67, 337, 434, 308, 698, 184, 449, 90, 500, 524, 120, 733, 233, 399, 89, 442, 938, 962, 877, 62, 786, 285, 377, 201, 873, 828, 333, 242, 691, 357, 546, 44, 668, 558, 183, 291, 456, 275, 718, 831, 994, 487, 532, 340, 416, 881, 437, 93, 509, 196, 411, 930, 584, 671, 362, 908, 981, 978, 73, 825, 438, 894, 516, 896, 510, 451, 722, 9, 654, 363, 16, 602, 228, 542, 928, 768, 208, 915, 560, 964, 937, 539, 508, 492, 392, 657, 612, 387, 415, 104, 191, 519, 43, 587, 158, 660, 559, 911, 854, 165, 826, 266, 24, 726, 616, 322, 155, 651, 481, 653, 42, 359, 77, 571, 20, 166, 151, 689, 248, 704, 639, 929, 53, 628, 400, 79, 249, 811, 418, 677, 378, 6, 818, 1, 860, 187, 394, 820, 993, 432, 538, 287, 925, 934, 975, 913, 548, 864, 621, 398, 882, 47, 159, 247, 457, 476, 431, 227, 940, 678, 710, 52, 251, 401, 102, 692, 770, 823, 241, 976, 185, 730, 604, 279, 138, 175, 132, 507, 367, 719, 591, 477, 264, 773, 19, 133, 58, 39, 942, 409, 898, 121, 68, 125, 506, 832, 203, 30, 916, 789, 490, 829, 277, 531, 327, 737, 526, 373, 336, 840, 150, 646, 598, 115, 330, 544, 315, 278, 874, 41, 46, 34, 545, 470, 905, 464, 518, 448, 824, 547, 238, 3, 91, 40, 561, 202, 553, 230, 239, 317, 912, 983, 935, 944, 673, 848, 21, 210, 863, 605, 766, 720, 708, 530, 353, 868, 65, 735, 84, 218, 724, 959, 364, 982, 396, 761, 341, 931, 793, 408, 140, 305, 875, 267, 839, 244, 410, 344, 27, 389, 843, 648, 676, 181, 283, 374, 810, 465, 943, 533, 939, 117, 853, 491, 274, 388, 263, 404, 801, 780, 594, 350, 514, 765, 259, 656, 496, 961, 688, 948, 124, 652, 575, 5, 213, 932, 626, 119, 778, 273, 631, 154, 395, 123, 311, 463, 182, 974, 716, 107, 100, 967, 556, 18, 460, 381, 535, 851, 971, 204, 623, 791, 703, 746, 835, 365, 240, 573, 72, 478, 206, 313, 354, 512, 617, 328, 219, 895, 787, 979, 892, 246, 459, 299, 647, 61, 220, 157, 236, 382, 335, 541, 31, 475, 112, 139, 446, 529, 261, 588, 635, 26, 921, 849, 189, 580, 436, 429, 713, 369, 147, 844, 430, 517, 856, 679, 190, 564, 672, 817, 174, 338, 702, 360, 347, 924, 618, 426, 923, 142, 570, 996, 947, 741, 687, 889, 619, 649, 469, 984, 497, 972, 225, 973, 257, 549, 777, 96, 355, 485, 503, 565, 919, 379, 884, 694, 862, 501, 63, 738, 301, 799, 209, 186, 130, 346, 603, 701, 402, 339, 522, 750, 585, 75, 756, 771, 179, 7, 33, 473, 173, 790, 25, 797, 45, 952, 809, 10, 428, 667, 425, 162, 59, 176, 574, 681, 816, 669, 126, 314, 725, 255, 950, 265, 94, 837, 665, 194, 256, 441, 29, 969, 957, 366, 552, 909, 834, 55, 641, 846, 316, 674, 699, 715, 997, 808, 867, 732, 557, 226, 714, 324, 211, 586, 527, 368, 152, 268, 505, 420, 745, 762, 798, 904, 886, 294, 833, 22, 633, 131, 50, 965, 838, 439, 686, 427, 391, 954, 776, 270, 753, 748, 215, 577, 450, 754, 767, 393, 878, 949, 149, 606, 885, 243, 871, 609, 592, 234, 630, 845, 92, 214, 700, 164, 622, 566, 144, 578, 624, 421, 329, 806, 711, 682, 38, 842, 262, 433, 739, 499, 850, 148, 567, 803, 794, 192, 471, 593, 122, 284, 534, 640, 951, 253, 178, 634, 872, 288, 706, 212, 351, 796, 980, 755, 709, 57, 758, 613, 600, 607, 663, 953, 583, 999, 483, 727, 986, 229, 946, 334, 764, 489, 815, 458, 540, 32, 188, 98, 608, 319, 830, 642, 893, 406, 655, 610, 852, 644, 153, 841, 280, 744],
#                [35, 781, 914, 611, 498, 989, 135, 814, 331, 88, 827]
# ]
#     position=np.load('position1000.npy')
    
    # solution1=solu[0]
    positions=first_x_rows[['ActualX','ActualY']]
    X = positions['ActualX'].tolist()
    Y= positions['ActualY'].tolist()    
    position=np.column_stack((X,Y)) 

    numsalesman=len(solution1)

    #产生需要的距离矩阵
    Data=Dataprocess(position)
    distmatrix=Data.build_dist_mat()#产生距离矩阵
    numsolution=1
    distcost_everysolution=np.zeros([numsolution,1])#储存每个解的总路程
    distcost=np.zeros([numsolution,numsalesman])#储存每个解中每个震源车所行路程

    for i, sol in enumerate([solution1]):
        for j, carsolution in enumerate(sol):
            dist=0
            if len(carsolution) > 1:
                dist = sum(distmatrix[carsolution[k]][carsolution[k + 1]] for k in range(len(carsolution) - 1))
            distcost[i, j] = dist
            distcost_everysolution[i] += dist

    testtime=max(distcost)/8.33
    testtime+=21*20

    TD=TDtotaltime()
    Tnewnowait=TD.Tcreate_array(solution1, 20, 8.33, distmatrix)
    Tnewcopy=TD.td_totaltime(solution1, 20, 8.33, distmatrix)

    def conditionjudge(second, Tlist, mtsp):
        movecar = []
        readycarindex = []
        readycarlocation = []
        workcarindex = []
        workcarlocation = []
        stopcarindex = []
        stopcarlocation = []

        for i, subT in enumerate(Tlist):
            if second >= subT.shape[1]:  
                continue
            if second + 1 >= subT.shape[1]:
                # Expand the array dynamically
                subT = np.pad(subT, ((0, 0), (0, 100)), 'constant')
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
                    location = nn

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

    def completejudge(second,T,stopcar,mtsp):
        
        stopnum=0#判断震源车停止没有
        stopcarfin=[]#储存停止工作的震源车
        for i in range(len(stopcar[0])):
            num=len(mtsp[stopcar[0][i]])
            
            if stopcar[1][i]==mtsp[stopcar[0][i]][num-1]:
                stopnum+=1
                stopcarfin.append(stopcar[0][i])
        return stopnum,stopcarfin

    def prof(T):
        y_time=[]
        x_dis=[]   
        movecar,readycarprevious,workcar,stopcar=conditionjudge(0, T, solution1)
        readycarprevious.append(0)
        
        numcompletecar=0#停止工作的车个数
        completecartime=[None]*len(T)#分别储存停止工作的车的总工作时间
            
        for second in range(0,100000000):
                movecar,readycar,workcar,stopcar=conditionjudge(second, T, solution1)
                complete,car=completejudge(second,T,stopcar,solution1)
                numcompletecar+=complete
                #判断所有车是否停止工作，停止直接停止循环，返回时间
                if numcompletecar!=0:
                    for k in range(len(car)):
                        completecartime[car[k]]=second
                if numcompletecar==len(T):
                    break
                #先储存这一秒准备激发的车之间的相互影响
                if len(readycar[0])>1:
                    for i in range(len(readycar[0])):
                        for j in range(i+1,len(readycar[0])):
                            y_time.append(0)
                            x_dis.append(distmatrix[readycar[1][i]][readycar[1][j]])
                #储存上一次激发和这次激发炮点之间的TD
                elif second!=0 and len(readycar[0])>0 and len(readycarprevious[0])>0:
                    for i in range(len(readycar[0])):
                        for j in range(len(readycarprevious[0])):
                            y_time.append(second-readycarprevious[2])
                            x_dis.append(distmatrix[readycar[1][i]][readycarprevious[1][j]])
                    readycarprevious[0]=readycar[0]
                    readycarprevious[1]=readycar[1]
                    readycarprevious[2]=second
        
        return x_dis,y_time



    x1_nodis,y1_notime=prof(Tnewnowait)
    x1_dis,y1_time=prof(Tnewcopy)
    x=[0,500,750,1000]
    # 计算函数值
    y =[7,7,0,0]
    # 绘制函数图像
    plt.figure(figsize=(8, 6),dpi=600)
    plt.plot(x, y, label='TD Rule')
    # filtered_points = [(xi, yi) for xi, yi in zip(x1_dis, y1_time) if 200<xi <= 1000 and yi<20]
    # filtered_x1, filtered_y1 = zip(*filtered_points) if filtered_points else ([], [])
    # filtered_points = [(xi, yi) for xi, yi in zip(x1_nodis, y1_notime) if 200<xi <= 1000 and yi<20]
    # filtered_x1no, filtered_y1no = zip(*filtered_points) if filtered_points else ([], [])
    # plt.scatter(filtered_x1, filtered_y1,color='red',marker='.', label='Shot Points With TD Model')
    plt.scatter( x1_nodis,y1_notime, color='black',marker='.', label='Shot Points Without TD Model')
    # 添加标题和标签
    plt.xlabel('Shot Point Spacing')
    plt.ylabel('Shot Time Interval')

    # 添加图例
    plt.legend()

    # 显示网格
    plt.grid(True)

    # 显示图形
    plt.show() 





         