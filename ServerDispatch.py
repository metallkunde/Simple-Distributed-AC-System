import time
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import ReadConfig


class Dispatch(QObject):
    changeSignal = pyqtSignal()  # 用于发射信号

    def __init__(self):
        super(Dispatch, self).__init__()

        self.queueS = []    # 服务队列
        self.queueW = []    # 等待队列
        self.roomIDA = 0    # 全局变量roomIDA代表经调度要从服务队列移到等待队列，停止送风的房间号，可直接读取
        self.roomIDB = 0    # 全局变量roomIDB代表经调度要从等待队列移到服务队列，开始送风的房间号，可直接读取
        self.speedA = 0     # roomIDA对应的风速（事实上始终为0）
        self.speedB = 0     # roomIDB对应的风速

        config = ReadConfig.Config.getDispatch()
        self.timeSpeed = int(config['speed'])       # 读入仿真速度
        self.queueSLen = int(config['quelen'])   # 读入队列长度
        self.waitTime = int(config['waittime'])     # 读入最长等待时间

    # 加入服务队列
    def addToServer(self, roomID, speedValue):
        dic = {'roomID': roomID, 'speed': speedValue, 'serverT': 0}
        self.queueS.append(dic)
        return self.queueS

    # 加入等待队列
    def addToWait(self, roomID, speedValue):
        dic = {'roomID': roomID, 'speed': speedValue, 'waitT': self.waitTime}
        self.queueW.append(dic)
        return self.queueW

    # 从服务队列移除
    def removeFromServer(self, roomID):
        for item in self.queueS:
            if item['roomID'] == roomID:
                self.queueS.remove(item)
                break

    # 从等待队列移除
    def removeFromWait(self, roomID):
        for item in self.queueW:
            if item['roomID'] == roomID:
                self.queueW.remove(item)
                break

    # 从等待队列移入服务队列
    def moveToServer(self, roomID):
        for item in self.queueW:
            if item['roomID'] == roomID:
                dic = item
                dic['serverT'] = 0
                self.queueS.append(dic)
                self.queueW.remove(item)
                break

    # 从服务队列移入等待队列
    def moveToWait(self, roomID):
        for item in self.queueS:
            if item['roomID'] == roomID:
                dic = item
                dic['waitT'] = self.waitTime
                self.queueW.append(dic)
                self.queueS.remove(item)
                break

    def addWaitTime(self, waitT):
        waittime = waitT - 1
        return waittime

    def addServerTime(self, serverT):
        servertime = serverT + 1
        return servertime

    def requestWind(self, roomID, speedValue):      # 返回值为4个参数，停止送风的房间号（若为0则代表没有），其风速（0），开始送风的房间号（若为0则代表没有），其风速
        flagS = 0   # 判断是否在服务队列重复房间
        flagW = 0   # 判断是否在等待队列重复房间
        loc = 0        # 记录重复房间在队列中的位置
        for i in range(len(self.queueS)):
            if self.queueS[i]['roomID'] == roomID:
                flagS = 1
                loc = i
                break
        for i in range(len(self.queueW)):
            if self.queueW[i]['roomID'] == roomID:
                flagW = 1
                loc = i
                break
        if flagS == 0 and flagW == 0:
            # 若服务队列未满
            if len(self.queueS) < self.queueSLen:
                self.addToServer(roomID, speedValue)
                return 0, 0, roomID, speedValue    # 表示接收请求，开始送风
            # 若服务队列满
            else:
                num = 0     # 记录服务队列中比请求风速小的房间的个数
                lowNum = 0
                midNum = 0
                for item in self.queueS:
                    if item['speed'] < speedValue:
                        num += 1
                for item in self.queueS:
                    if item['speed'] == 1:
                        lowNum += 1
                    elif item['speed'] == 2:
                        midNum += 1
                # 服务队列中至少有一个房间风速小于新请求
                if num >= 1:
                    # 服务队列至少有一个低风速
                    if lowNum >= 1:
                        for item in self.queueS:
                            if item['speed'] == 1:
                                roomIDO = item['roomID']
                                self.moveToWait(roomIDO)
                                self.addToServer(roomID, speedValue)
                                return roomIDO, 0, roomID, speedValue
                    elif lowNum == 0 and midNum >= 1:
                        for item in self.queueS:
                            if item['speed'] == 2:  # 队列中第一个中风速即为中风速里（最低优先级）服务时间最久的，将该房间加入等待队列
                                roomIDO = item['roomID']
                                self.moveToWait(roomIDO)
                                self.addToServer(roomID, speedValue)
                                return roomIDO, 0, roomID, speedValue
                # 服务队列中房间风速都大于等于新请求
                else:
                    self.addToWait(roomID, speedValue)
                    return roomID, 0, 0, 0  # 表示拒绝请求，放入等待队列

        elif flagS == 1:
            highNum = 0  # 等待队列中高风请求的个数
            midNum = 0  # 等待队列中中风请求的个数
            # 若等待队列不为空
            if len(self.queueW) != 0:
                # 风速比原来升高或不变
                if speedValue > self.queueS[loc]['speed'] or speedValue == self.queueS[loc]['speed']:
                    self.queueS[loc]['speed'] = speedValue
                    return 0, 0, roomID, speedValue
                # 风速比原来降低
                elif speedValue < self.queueS[loc]['speed']:
                    num = 0     # 记录等待队列中比请求风速大的房间的个数
                    for item in self.queueW:
                        if item['speed'] > speedValue:
                            num += 1
                    for item in self.queueW:
                        if item['speed'] == 3:
                            highNum += 1
                        elif item['speed'] == 2:
                            midNum += 1
                    # 等待队列中至少有一个房间风速大于新请求
                    if num >= 1:
                        # 等待队列至少有一个高风速
                        if highNum >= 1:
                            for item in self.queueW:
                                if item['speed'] == 3:  # 队列中第一个高风速即为高风速里（最高优先级）等待时间最久的，将该房间加入服务队列
                                    roomIDO = item['roomID']
                                    speedO = item['speed']
                                    self.removeFromServer(roomID)
                                    self.addToWait(roomID, speedValue)
                                    self.moveToServer(roomIDO)
                                    return roomID, 0, roomIDO, speedO
                        # 等待队列无高风速，至少有一个中风速
                        elif highNum == 0 and midNum >= 1:
                            for item in self.queueW:
                                if item['speed'] == 2:  # 队列中第一个中风速即为中风速里（最高优先级）等待时间最久的，将该房间加入服务队列
                                    roomIDO = item['roomID']
                                    speedO = item['speed']
                                    self.removeFromServer(roomID)
                                    self.addToWait(roomID, speedValue)
                                    self.moveToServer(roomIDO)
                                    return roomID, 0, roomIDO, speedO

                    # 等待队列中的风速都小于等于新请求
                    else:
                        self.queueS[loc]['speed'] = speedValue      # 允许发出请求的房间送风，在服务队列更改风速值
                        return 0, 0, roomID, speedValue
            # 若等待队列为空
            else:
                self.queueS[loc]['speed'] = speedValue      # 允许发出请求的房间送风，在服务队列更改风速值
                return 0, 0, roomID, speedValue

        elif flagW == 1:
            lowNum = 0  # 服务队列中低风请求的个数
            midNum = 0  # 服务队列中中风请求的个数
            # 此时等待队列必不为空，不用考虑为空的情况
            # 风速比原来降低或不变
            if speedValue < self.queueW[loc]['speed'] or speedValue == self.queueW[loc]['speed']:
                self.queueW[loc]['speed'] = speedValue
                return roomID, 0, 0, 0
            # 风速比原来升高
            elif speedValue > self.queueW[loc]['speed']:
                num = 0     # 记录服务队列中比请求风速小的房间的个数
                for item in self.queueS:
                    if item['speed'] < speedValue:
                        num += 1
                for item in self.queueS:
                    if item['speed'] == 1:
                        lowNum += 1
                    elif item['speed'] == 2:
                        midNum += 1
                # 服务队列中至少有一个房间风速小于新请求
                if num >= 1:
                    # 服务队列至少有一个低风速
                    if lowNum >= 1:
                        for item in self.queueS:
                            if item['speed'] == 1:  # 队列中第一个低风速即为低风速里（最低优先级）服务时间最久的，将该房间加入等待队列
                                roomIDO = item['roomID']
                                self.moveToWait(roomIDO)
                                self.removeFromWait(roomID)
                                self.addToServer(roomID, speedValue)
                                return roomIDO, 0, roomID, speedValue
                    # 服务队列无低风速，至少有一个中风速
                    elif lowNum == 0 and midNum >= 1:
                        for item in self.queueS:
                            if item['speed'] == 2:  # 队列中第一个中风速即为中风速里（最低优先级）服务时间最久的，将该房间加入等待队列
                                roomIDO = item['roomID']
                                self.moveToWait(roomIDO)
                                self.removeFromWait(roomID)
                                self.addToServer(roomID, speedValue)
                                return roomIDO, 0, roomID, speedValue

                # 服务队列中的风速都大于等于新请求
                else:
                    self.queueW[loc]['speed'] = speedValue
                    return roomID, 0, 0, 0

    def stopWind(self, roomID):     # 返回值为4个参数，停止送风的房间号，其风速（0），开始送风的房间号（若为0则代表没有），其风速
        flag = 0
        for item in self.queueS:
            if roomID == item['roomID']:
                flag = 1
                break
        # 若该房间号已经在服务队列中
        if flag == 1:
            self.removeFromServer(roomID)
            highNum = 0     # 等待队列中高风请求的个数
            midNum = 0      # 等待队列中中风请求的个数
            # 若等待队列不为空
            if len(self.queueW) != 0:
                for item in self.queueW:
                    if item['speed'] == 3:
                        highNum += 1
                    elif item['speed'] == 2:
                        midNum += 1
                if highNum >= 1:   # 等待队列至少有一个高风速，将等待时间最长的加入服务队列
                    for item in self.queueW:
                        if item['speed'] == 3:  # 队列中第一个高风速即为高风速里（最高优先级）等待时间最久的，将该房间加入服务队列
                            roomIDO = item['roomID']
                            speedO = item['speed']
                            self.moveToServer(roomIDO)
                            return roomID, 0, roomIDO, speedO
                elif highNum == 0 and midNum >= 1:   # 等待队列无高风速，至少有一个中风速，将等待时间最长的加入服务队列
                    for item in self.queueW:
                        if item['speed'] == 2:  # 队列中第一个中风速即为中风速里（最高优先级）等待时间最久的，将该房间加入服务队列
                            roomIDO = item['roomID']
                            speedO = item['speed']
                            self.moveToServer(roomIDO)
                            return roomID, 0, roomIDO, speedO
                else:   # 等待队列全为低风速
                    for item in self.queueW:
                        if item['speed'] == 1:  # 队列中第一个低风速即为低风速里（最高优先级）等待时间最久的，将该房间加入服务队列
                            roomIDO = item['roomID']
                            speedO = item['speed']
                            self.moveToServer(roomIDO)
                            return roomID, 0, roomIDO, speedO
            # 若等待队列为空
            else:
                return roomID, 0, 0, 0
        # 若该房间号不在等待队列中
        else:
            return roomID, 0, 0, 0

    def updateQueue(self):
        while True:
            time.sleep(1/self.timeSpeed)
            for item in self.queueS:
                item['serverT'] = self.addServerTime(item['serverT'])
            for item in self.queueW:
                item['waitT'] = self.addWaitTime(item['waitT'])
            for item in self.queueW:
                if item['waitT'] <= 0:
                    if item['speed'] == self.queueS[0]['speed']:
                        self.roomIDA = self.queueS[0]['roomID']    # roomIDA代表经调度要从服务队列移到等待队列，停止送风的房间号
                        self.roomIDB = item['roomID']              # roomIDB代表经调度要从等待队列移到服务队列，开始送风的房间号
                        self.speedA = 0
                        self.speedB = item['speed']
                        self.moveToWait(self.queueS[0]['roomID'])
                        self.moveToServer(item['roomID'])
                        break

                    elif item['speed'] == self.queueS[1]['speed']:
                        self.roomIDA = self.queueS[1]['roomID']
                        self.roomIDB = item['roomID']
                        self.speedA = 0
                        self.speedB = item['speed']
                        self.moveToWait(self.queueS[1]['roomID'])
                        self.moveToServer(item['roomID'])
                        break

                    elif item['speed'] == self.queueS[2]['speed']:
                        self.roomIDA = self.queueS[1]['roomID']
                        self.roomIDB = item['roomID']
                        self.speedA = 0
                        self.speedB = item['speed']
                        self.moveToWait(self.queueS[2]['roomID'])
                        self.moveToServer(item['roomID'])
                        break

                    else:
                        self.roomIDA = 0
                        self.roomIDB = 0
                        self.speedA = 0
                        self.speedB = 0
                else:
                    self.roomIDA = 0
                    self.roomIDB = 0
                    self.speedA = 0
                    self.speedB = 0

            self.changeSignal.emit()    # 发送更新信号
