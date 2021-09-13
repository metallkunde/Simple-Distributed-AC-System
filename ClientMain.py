from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import ClientUI
from ClientHandler import ClientHandler
import UDPClient
import time
import TempControl
import threading
import StopThreading
import sys
import socket
import PyQt5.sip


class Main(ClientUI.ClientWindow):
    def __init__(self, roomID):
        super(Main, self).__init__()
        self.handler = ClientHandler(self)
        self.link = False               # 连接状态
        self.open = False               # 空调开启状态
        self.roomID = roomID            # 房间号
        self.sp_num = 0                 # 传输风速
        self.require = 0                # 是否受到请求
        self.stop = 0                   # 主动停止
        self.delay_flag = 0             # 延迟设置标志位
        self.delay_time = 2             # 延迟设置时间
        self.udpConnect = UDPClient.UdpClient(self.signal_write_msg)  # UDP连接
        self.TempControl = TempControl.TempControl(self.roomID)  # 温度控制线程
        self.changeTemp_th = threading.Thread(target=self.TempControl.changeTemp)
        self.changeTemp_th.start()  # 开启温控模拟线程
        self.getHostip()        # 获取服务器ip并显示（本机便于调试）
        self.connectSignal()    # 所有信号槽连接

    # 信号槽连接
    def connectSignal(self):
        self.sendSpeedTempButton.clicked.connect(self.delaySend) # 发送设置delaySend  self.
        self.connectButton.clicked.connect(self.connectServer)      # 连接服务器
        self.openButton.clicked.connect(self.startAirConditon)      # 空调开机
        self.closeButton.clicked.connect(self.closeAirConditon)     # 空调关机
        self.TempControl.changeSignal.connect(self.stateRenew)      # 温控信号

    # 获取当前ip并显示
    def getHostip(self):
        self.handler.getHostip()

    # 根据按钮设定风速、温度并进行显示
    def setParemeter(self):
        self.handler.setParemeter()

    # 延时设置，若1s内无新设置动作产生，则写入当前设置
    def timeCount(self):
        self.handler.timeCount()

    # 控制设置延迟的线程，点击设置按钮时调用
    def delaySend(self):
        # 若新的设置动作触发时没有设置在等待更新
        if self.delay_flag == 0:
            self.delay_th = threading.Thread(target=self.timeCount)     # 开启新线程
            self.delay_th.start()
        # 若新的设置动作触发时有设置正在等待更新
        else:
            print("指令覆盖")
            StopThreading.stop_thread(self.delay_th)    # 停止旧线程
            self.delay_th = threading.Thread(target=self.timeCount)     # 开启新线程
            self.delay_th.start()

    # 接收温度控制器的信号，进行界面上的更新，并且将自身状态发送给服务端
    def stateRenew(self):
        self.handler.stateRenew()

    # 与服务器连接or断开连接的请求
    def connectServer(self):
        if not self.link:
            ip = self.ipLineEdit.text()
            port = self.portLineEdit.text()

            if self.udpConnect.udp_client_start(ip, port, self.handler.setRoomID()):
                self.link = True
                self.openButton.setEnabled(True)
                self.connectButton.setText("断开连接")
                self.TempControl.totalCost = 0
            else:
                self.connectButton.setChecked(False)
        else:
            self.udpConnect.udp_send('* bye ' + str(self.roomID))
            print('向主机发送了断开请求' + '* bye ' + str(self.roomID))
            self.udpConnect.udp_client_close()
            self.connectButton.setText("连接")
            self.openButton.setEnabled(False)
            self.closeButton.setEnabled(False)
            self.link = False

    def isOpen(self):
        return self.open

    # 空调开机，启动温控线程
    def startAirConditon(self):
        if not self.isOpen():
            self.handler.startAirConditon()


    # 空调关机
    def closeAirConditon(self):
        if self.isOpen():
            self.handler.closeAirConditon()

    # 显示客户端接受信息，并且分析作出相应动作
    def write_msg(self, msg):
        self.udpLineEdit.setText(msg)  # 显示
        if '!' in msg:
            str2 = msg.split(' ')
            msgroom = str2[1]
            msgspeed = str2[2]
            if msgroom == str(self.roomID):
                if msgspeed != '0':
                    self.TempControl.runState = 'run'
                    self.require = 1
                #  调度队列返回执行命令
                else:
                    if self.stop == 1:
                        self.TempControl.runState = 'sleep'
                    else:
                        self.TempControl.runState = 'waiting'
                self.require = 1
                self.stop = 0
                #  调度队列返回等待命令
        if 'bye' in msg:
            QMessageBox.critical(self, '连接错误', '服务器断开连接')
            self.connectButton.setEnabled(True)
            self.sendSpeedTempButton.setEnabled(False)
            self.connectServer()

        if '#' in msg:
            msglist = msg.split(' ')
            # 状态显示修改
            self.stateLabel.setText('模式:' + msglist[1])

            # 温度控制模块修改
            self.TempControl.tempSet = int(msglist[2])
            self.TempControl.runModel = msglist[1]

            # ui界面温度设置范围修改——此处限制了温度设定会根据模式在范围内
            if self.TempControl.runModel == 'cool':
                self.sp.setMinimum(18)
                self.sp.setMaximum(self.TempControl.tempDefault)
            elif self.TempControl.runModel == 'warm':
                self.sp.setMinimum(self.TempControl.tempDefault)
                self.sp.setMaximum(30)

    # 鼠标点击关闭动作
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            '退出',
            "确定要退出吗",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用
        if reply == QMessageBox.Yes:
            if self.open:
                self.udpConnect.udp_send("* close " + str(self.roomID))
                print('向主机发送了关机请求' + "* close " + str(self.roomID))
            if self.link:
                self.udpConnect.udp_send('* bye ' + str(self.roomID))
                print('向主机发送了断开连接请求' + '* bye ' + str(self.roomID))
                self.udpConnect.udp_client_close()
            StopThreading.stop_thread(self.changeTemp_th)
            event.accept()
        else:
            event.ignore()
