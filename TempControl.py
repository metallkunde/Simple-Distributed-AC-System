
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import time
import ReadConfig


class TempControl(QObject):
    changeSignal = pyqtSignal()  # 用于发射信号

    def __init__(self, roomID):
        super(TempControl, self).__init__()
        self.roomID = roomID
        self.tempConfig = ReadConfig.Config.getTempcontrol()    # 读入控制模块参数
        self.beginConfig = ReadConfig.Config.getBegintemp()     # 读入初始温度
        self.timeSpeed = int(self.tempConfig['speed'])          # 设置仿真速度
        self.refreshSeq = int(self.tempConfig['refreshseq'])    # 温度更新频率,10以上可以保证不会出现不连续的琴科给
        self.highPrice = float(self.tempConfig['highprice'])    # 高风费率
        self.midPrice = float(self.tempConfig['midprice'])      # 中风费率
        self.lowPrice = float(self.tempConfig['lowprice'])      # 低风费率
        self.highDelta = float(self.tempConfig['highdelta'])    # 高风温度变化率
        self.midDelta = float(self.tempConfig['middelta'])      # 中风温度变化率
        self.lowDelta = float(self.tempConfig['lowdelta'])      # 低风温度变化率
        self.tempDefault = int(self.beginConfig['room' + str(self.roomID)])     # 省缺温度
        self.tempNow = int(self.beginConfig['room' + str(self.roomID)])         # 室内温度
        self.tempSet = 25           # 默认温度 25°
        self.speedSet = 'mid'       # 默认风速 high mid low
        self.runModel = 'cool'      # 默认运行状态 cool warm
        self.runState = 'close'     # 用于指示是否运行 run close sleep waiting sleeping
        self.totalCost = 0          # 计费

    def setDefault_Now(self):
        self.tempDefault = int(self.config['room' + str(self.roomID)])
        self.tempNow = int(self.config['room' + str(self.roomID)])

    # 模式设置函数
    def setModel(self, model):
        self.runModel = model

    # 风速设置函数
    def setSpeed(self, speed):
        self.speedSet = speed

    # 温度设置函数
    def setTemp(self, temp):
        self.tempSet = temp
        return 1

    # 用信号定时触发该函数，一定频率进行改变
    def changeTemp(self):
        while True:
            time.sleep(60 / self.refreshSeq / self.timeSpeed)
            if self.runState == 'run':
                if self.runModel == "cool" and self.tempNow <= self.tempSet:  # 温度相等停止变化
                    self.runState = 'sleeping'

                elif self.runModel == "warm" and self.tempNow >= self.tempSet:  # 温度相等停止变化
                    self.runState = 'sleeping'

                elif self.runModel == "cool" and self.tempNow > self.tempSet:  # 制冷模式下
                    if self.speedSet == 'high':
                        self.tempNow -= self.highDelta / self.refreshSeq
                        self.totalCost += self.highPrice / self.refreshSeq
                    elif self.speedSet == 'mid':
                        self.tempNow -= self.midDelta / self.refreshSeq
                        self.totalCost += self.midPrice / self.refreshSeq
                    elif self.speedSet == 'low':
                        self.tempNow -= self.lowDelta / self.refreshSeq
                        self.totalCost += self.lowPrice / self.refreshSeq
                elif self.runModel == "warm" and self.tempNow < self.tempSet:  # 制热模式下
                    if self.speedSet == 'high':
                        self.tempNow += self.highDelta / self.refreshSeq
                        self.totalCost += self.highPrice / self.refreshSeq
                    elif self.speedSet == 'mid':
                        self.tempNow += self.midDelta / self.refreshSeq
                        self.totalCost += self.midPrice / self.refreshSeq
                    elif self.speedSet == 'low':
                        self.tempNow += self.lowDelta / self.refreshSeq
                        self.totalCost += self.lowPrice / self.refreshSeq

            elif self.runState == 'sleep':
                if self.runModel == "cool" and (self.tempNow - self.tempSet) >= 1:  # 温度相等停止变化
                    # self.runState = 'run'
                    self.runState = 'waiting'
                elif self.runModel == "warm" and (self.tempSet - self.tempNow) >= 1:  # 温度相等停止变化
                    # self.runState = 'run'
                    self.runState = 'waiting'
                elif self.tempNow < self.tempDefault:
                    self.tempNow += 0.5 / self.refreshSeq
                elif self.tempNow > self.tempDefault:
                    self.tempNow -= 0.5 / self.refreshSeq

            elif self.runState == 'waiting':
                if self.tempNow < self.tempDefault:
                    self.tempNow += 0.5 / self.refreshSeq
                elif self.tempNow > self.tempDefault:
                    self.tempNow -= 0.5 / self.refreshSeq

            elif self.runState == 'close':
                if self.tempNow < self.tempDefault:
                    self.tempNow += 0.5 / self.refreshSeq
                elif self.tempNow > self.tempDefault:
                    print(self.tempNow, self.tempDefault)
                    self.tempNow -= 0.5 / self.refreshSeq

            # 精度处理

            # 对于温度和金额的精度进行处理

            # 发送更新信号
            self.changeSignal.emit()

