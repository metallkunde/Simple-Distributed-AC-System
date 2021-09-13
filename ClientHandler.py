import socket
import time
from PyQt5.QtWidgets import *


class ClientHandler():
    def __init__(self, window):
        self.window = window

    # 设置房间id
    def setRoomID(self):
        self.window.w_roomID.display(self.window.roomID)
        return self.window.roomID

    def setParemeter(self):
        str_speed = ''
        if self.window.radio1.isChecked():
            str_speed = "high"
            self.window.sp_num = 3
        elif self.window.radio2.isChecked():
            str_speed = "mid"
            self.window.sp_num = 2
        elif self.window.radio3.isChecked():
            str_speed = "low"
            self.window.sp_num = 1

        # 温度控制模块设置
        self.window.TempControl.setSpeed(str_speed)
        self.window.TempControl.setTemp(self.window.sp.value())
        query_msg = "? " + str(self.window.roomID) + ' ' + str(self.window.sp_num)
        self.window.udpConnect.udp_send(query_msg)
        self.window.TempControl.runState = 'waiting'
        # print('向主机发送了送风请求' + query_msg)
        self.window.speedstateLabel.setText('风速:' + str_speed)

    def getHostip(self):
        my_addr = socket.gethostbyname(socket.gethostname())
        self.window.ipLineEdit.setText(str(my_addr))
        self.window.portLineEdit.setValue(2222)

    # 延时设置，若1s内无新设置动作产生，则写入当前设置
    def timeCount(self):
        self.window.delay_flag = 1
        time.sleep(self.window.delay_time)
        self.setParemeter()
        print("设置成功")
        self.window.delay_flag = 0

    # 接收温度控制器的信号，进行界面上的更新，并且将自身状态发送给服务端
    def stateRenew(self):
        # 更新ui界面——温度
        self.setRoomID()
        temp = ("%.1f" % self.window.TempControl.tempNow)
        self.window.tempLcd.display(temp)
        # 更新显示金额*********
        cost = ("%.2f" % self.window.TempControl.totalCost)
        self.window.bill.display(str(cost))
        # 启动时温控就会开始工作，只有连接服务器时才向服务器发送
        if self.window.link:
            message = '#' + ' ' + str(self.window.roomID) + " " + str(self.window.TempControl.runState) + ' ' + str(
                temp) + " " + \
                      str(self.window.TempControl.tempSet) + " " + str(
                self.window.TempControl.speedSet) + ' ' + str(
                cost)
            self.window.udpConnect.udp_send(message)
            # print('向主机发送了当前状态' + message)
            if self.window.TempControl.runState == 'waiting':
                if self.window.require == 0:
                    query_msg = "? " + str(self.window.roomID) + ' ' + str(self.window.sp_num)
                    self.window.udpConnect.udp_send(query_msg)
                    # print('向主机发送了送风请求' + query_msg)
            if self.window.TempControl.runState == 'sleeping':
                if self.window.require == 0:
                    stop_msg = "? " + str(self.window.roomID) + ' ' + str(0)
                    self.window.udpConnect.udp_send(stop_msg)
                    # print('向主机发送了停止送风请求' + stop_msg)
                    self.window.stop = 1
            self.window.require = 0

    def startAirConditon(self):
        self.window.udpConnect.udp_send("* start " + str(self.setRoomID()))
        print('向主机发送了开机请求' + "* start " + str(self.setRoomID()))
        # 开机重新设置参数
        self.window.radio2.setChecked(True)
        self.window.sp.setValue(25)
        self.setParemeter()

        query_msg = "? " + str(self.setRoomID()) + ' ' + str(self.window.sp_num)  # 调度请求由房间号，风度组成
        self.window.udpConnect.udp_send(query_msg)  # 发送启动请求
        print('向主机发送了送风请求' + str(self.setRoomID()) + str(self.window.sp_num))

        self.window.TempControl.runState = 'waiting'
        self.window.openButton.setEnabled(False)
        self.window.closeButton.setEnabled(True)
        self.window.sendSpeedTempButton.setEnabled(True)
        self.window.connectButton.setEnabled(False)
        self.window.open = True

    def closeAirConditon(self):
        self.window.udpConnect.udp_send("* close " + str(self.window.roomID))
        print('向主机发送了关机请求' + "* close " + str(self.window.roomID))
        self.window.TempControl.runState = 'close'
        self.window.openButton.setEnabled(True)
        self.window.closeButton.setEnabled(False)
        self.window.sendSpeedTempButton.setEnabled(False)
        self.window.connectButton.setEnabled(True)
        self.window.open = False

    def write_msg(self, msg):
        self.window.udpLineEdit.setText(msg)  # 显示
        if '!' in msg:
            str2 = msg.split(' ')
            msgroom = str2[1]
            msgspeed = str2[2]
            if msgroom == str(self.window.roomID):
                if msgspeed != '0':
                    self.window.TempControl.runState = 'run'
                    self.window.require = 1
                #  调度队列返回执行命令
                else:
                    if self.window.stop == 1:
                        self.window.TempControl.runState = 'sleep'
                    else:
                        self.window.TempControl.runState = 'waiting'
                self.window.require = 1
                self.window.stop = 0
                #  调度队列返回等待命令
        if 'bye' in msg:
            QMessageBox.critical(self.window, '连接错误', '服务器断开连接')
            self.window.connectButton.setEnabled(True)
            self.window.sendSpeedTempButton.setEnabled(False)
            self.window.connectServer()

        if '#' in msg:
            msglist = msg.split(' ')
            # 状态显示修改
            self.window.stateLabel.setText('模式:' + msglist[1])

            # 温度控制模块修改
            self.window.TempControl.tempSet = int(msglist[2])
            self.window.TempControl.runModel = msglist[1]

            # ui界面温度设置范围修改——此处限制了温度设定会根据模式在范围内
            if self.window.TempControl.runModel == 'cool':
                self.window.sp.setMinimum(18)
                self.window.sp.setMaximum(self.window.TempControl.tempDefault)
            elif self.window.TempControl.runModel == 'warm':
                self.window.sp.setMinimum(self.window.TempControl.tempDefault)
                self.window.sp.setMaximum(30)