import time
from PyQt5.QtWidgets import *
import UDPServer
import ServerUI
import ServerDispatch
import ReadConfig
import socket
import threading
import StopThreading
import Utils
import sys
from Log import Log
from Statement import DailyStatement, MonthlyStatement, AnnualStatement, WeeklyStatment
from Mapper import Mapper


class Main(ServerUI.ServerWindow):
    """
    server
    """
    def __init__(self):
        super(Main, self).__init__()

        self.udpConnect = UDPServer.UdpServer(self.signal_write_msg)  # UDP
        self.dispatch = ServerDispatch.Dispatch()
        self.updateQueue_th = threading.Thread(target=self.dispatch.updateQueue)
        self.updateQueue_th.start()
        self.serverTest_th = threading.Thread(target=self.beginTest)
        self.connectSignal()
        self.getHostip()
        self.mapper = Mapper()
        self.mapper.connect()
        self.log = Log(self.mapper)

    def write_on_off_msg(self, msg):
        """
        写入开关连接控制请求
        :param msg:
        """
        str1 = msg.split(' ')
        room = str1[6]
        if self.judge_write_on_off_msg(str1) == 'hi':
            self.set_on_off_hi_msg(room, (str(str1[1]), int(str1[3])))
        if self.judge_write_on_off_msg(str1) == 'start':
            self.set_on_off_start_msg(room)
        elif self.judge_write_on_off_msg(str1) == 'close':
            self.set_on_off_close_msg(room)
        elif self.judge_write_on_off_msg(str1) == 'bye':
            self.set_on_off_bye_msg(room)

    def judge_write_on_off_msg(self, msg):
        """
        取出massage
        :param msg:
        :return:
        """
        return msg[5]

    def write_temperature_msg(self, msg):
        """
        将温度请求写入
        :param msg:
        """
        if len(self.dispatch.queueW) != 0 and self.get_dispatch_stop_room() != 0:
            self.write_temperature_msg_when_queue()
        str0 = msg.split('#')[1].split(' ')
        for i in range(6):
            self.tablewidget1.setItem(int(str0[1]) - 1, i, QTableWidgetItem(str0[i + 1]))

    def write_temperature_msg_when_queue(self):
        """
        当队列存在元素时写入温度请求
        """
        dispatch_stop_message = self.get_wind_msg_str(self.get_dispatch_stop_room(),
                                                      self.get_dispatch_stop_speed())
        print('主机发送调度指令:停机房间号：' + dispatch_stop_message)
        self.udpConnect.address = self.udpConnect.connectClient[str(self.get_dispatch_stop_room())]
        self.udpConnect.udp_send(dispatch_stop_message)
        self.log.insert_log(dispatch_stop_message)

    def get_dispatch_stop_speed(self):
        """
        :return:
        """
        return self.dispatch.speedA

    def get_dispatch_stop_room(self):
        """
        :return:
        """
        return self.dispatch.roomIDA

    def connectSignal(self):
        """
        连接信号槽
        """
        self.setButton.clicked.connect(self.setParemeter)
        self.getipButton.clicked.connect(self.getHostip)
        self.startButton.clicked.connect(self.startServer)
        self.stopButton.clicked.connect(self.closeServer)
        self.setDayButton.clicked.connect(self.write_day_table)  # 日报表
        self.setWeekButton.clicked.connect(self.write_week_table)  # 周报表
        self.setMonButton.clicked.connect(self.write_mon_table)  # 月报表
        self.setYearButton.clicked.connect(self.write_year_table)  # 年报表
        self.dispatch.changeSignal.connect(self.renewSeque)  # 刷新队列
        self.dispatch.changeSignal.connect(self.dispatchRenew)  # 更新调度
        self.billOutButton.clicked.connect(self.outputBill)

    def set_on_off_start_msg(self, room):
        """
        发送开关的打开请求
        :param room:
        """
        self.tablewidget1.setItem(int(room) - 1, 1, QTableWidgetItem('start'))

    def set_on_off_close_msg(self, room):
        """
        发送开关的关闭请求
        :param room:
        """
        self.tablewidget1.setItem(int(room) - 1, 1, QTableWidgetItem('close'))
        self.dispatch.stopWind(int(room))

    def set_on_off_bye_msg(self, room):
        """
        发送开关的bye请求
        :param room:
        """
        self.log.del_last_msg(room)
        self.tablewidget1.setItem(int(room) - 1, 1, QTableWidgetItem('disconnected'))
        del self.udpConnect.connectClient[room]
        for i in range(2, 6):
            self.tablewidget1.setItem(int(room) - 1, i, QTableWidgetItem(''))
        self.write_bill(room)

    def set_on_off_hi_msg(self, room, tuples):
        """
        测试开关
        :param room:
        :param tuples:
        """
        if not self.udpConnect.connectClient.__contains__(room):
            self.udpConnect.connectClient[room] = tuples
            self.sendParemeter()
        if len(self.udpConnect.connectClient) == 5:
            print("********** BEGIN TEST **********")
            # 调整仿真速度
            if int(ReadConfig.Config.getTest()['flag']) == 1:
                self.udpConnect.udp_sendall('test')  # 发送测试指令
                self.serverTest_th.start()

    def outputBill(self):
        """
        打印所有账单
        """
        output = open('./bill/bill.xls', 'w', encoding='gbk')
        output.write('房间号\t入住时间\t离店时间\t消费总金额\t耗电量\n')
        for i in range(self.tablewidget31.rowCount()):  # 当前帐单长度
            for j in range(5):
                output.write(str(self.tablewidget31.item(i, j).text()))  # 写界面上对应表格的内容
                output.write('\t')
            output.write('\n')  # 写完一行立马换行
        output.close()

    def renewSeque(self):
        """
        将两个队列显示在界面
        """
        self.read_queue(self.tablewidget4, self.dispatch.queueS, 'serverT')
        self.read_queue(self.tablewidget5, self.dispatch.queueW, 'waitT')

    def getHostip(self):
        """
        获取当前ip并显示
        """
        self.ipLineEdit.setText(str(socket.gethostbyname(socket.gethostname())))


    def show_table_on_ui(self, tablewidget, b, e, detail, total, cnt):
        """
        在界面上显示日报表/详单
        :param tablewidget:
        :param b:
        :param e:
        :param detail:
        :param total:
        :param cnt:
        """
        detail_list = list(list(items) for items in list(detail))
        for i in range(len(detail_list)):
            for j in range(len(detail_list[i])):
                detail_list[i][j] = Utils.float_to_round(detail_list[i][j], 2)
                tablewidget.setItem(i, j, QTableWidgetItem(str(detail_list[i][j])))
        fee, electricity = total
        Utils.fee_show_table_on_ui(b, fee)
        self.electricity_show_table_on_ui(e, electricity)

    def electricity_show_table_on_ui(self, e, electricity):
        """
        展示电力
        :param e:
        :param electricity:
        """
        if electricity is not None:
            e.setText(str(round(electricity, 3)))  # 电量保留三位小数
        else:
            e.setText("暂无数据")

    def write_day_table(self):
        """
        针对每天
        获取查询报表的时间范围，和两个总量
        """
        table = DailyStatement(Utils.t_day(self.datetimeEdit21))
        table.getDetail()
        table.getTotal()
        if table.verbose:
            print("***", table.detail, table.total)
        self.show_table_on_ui(self.tablewidget21, self.bill2, self.electricity2,
                              table.detail, table.total, table.list_row_cnt)

    def write_week_table(self):
        """
        针对每周
        获取查询报表的时间范围，和两个总量
        """
        table = WeeklyStatment(str(self.week.value()))
        table.getDetail()
        table.getTotal()
        if table.verbose:
            print("***", table.detail, table.total)
        self.show_table_on_ui(self.tablewidget22, self.bill2, self.electricity2,
                              table.detail, table.total, table.list_row_cnt)

    def write_mon_table(self):
        """
        针对每月
        获取查询报表的时间范围，和两个总量
        """
        table = MonthlyStatement(Utils.t_month(self.datetimeEdit22))  # 目前没用到返回值
        table.getDetail()
        table.getTotal()
        if table.verbose:
            print(table.detail, table.total)
        self.show_table_on_ui(self.tablewidget23, self.bill2, self.electricity2,
                              table.detail, table.total, table.list_row_cnt)

    def write_year_table(self):
        """
        针对每年
        获取查询报表的时间范围，和两个总量
        """
        table = AnnualStatement(Utils.t_year(self.datetimeEdit23))
        table.getDetail()
        table.getTotal()
        if table.verbose:
            print(table.detail, table.total)
        self.show_table_on_ui(self.tablewidget24, self.bill2, self.electricity2,
                              table.detail, table.total, table.list_row_cnt)

    def write_bill(self, room):
        """
        此函数在收到bye消息时被调用
        计算账单详单
        :param room: 房间号
        """
        r = Utils.get_receipt(room)
        self.write_bill_to_tablewidget31(r)
        self.write_bill_to_tablewidget32(r)
        self.write_bill_to_de_b_text(r)
        self.write_bill_to_de_e_text(r)

    def write_bill_to_de_e_text(self, r):
        """
        计算账单详单到de_e_text
        :param r: 账单详单
        """
        self.de_e_Text.clear()
        self.de_e_Text.setText(str(round(r.total[1], 3)))

    def write_bill_to_de_b_text(self, r):
        """
        计算账单详单到de_b_text
        :param r: 账单详单
        """
        self.de_b_Text.clear()
        self.de_b_Text.setText(str(round(r.total[0], 2)))


    def write_bill_to_tablewidget32(self, r):
        """
        计算账单详单到tablewidget31
        :param r: 账单详单
        """
        self.tablewidget32.clearContents()  # 表格和框框每次写之前先清空
        bill_list = list(list(items) for items in list(r.detail))
        self.tablewidget32.setRowCount(len(bill_list))
        for i in range(0, len(bill_list)):
            self.tablewidget32.setItem(i, 0, QTableWidgetItem(bill_list[i][0]))  # 房间号
            for j in range(1, 4):  # 1-3分别是开始送风时间、结束送风时间、送风时长
                self.tablewidget32.setItem(i, j, QTableWidgetItem(str(bill_list[i][j]).split('.')[0]))
            self.tablewidget32.setItem(i, 4, QTableWidgetItem(bill_list[i][4]))  # 风速
            self.tablewidget32.setItem(i, 5, QTableWidgetItem(str(bill_list[i][5])))  # 费率
            self.tablewidget32.setItem(i, 6, QTableWidgetItem(str(round(float(bill_list[i][6]), 2))))

    def write_bill_to_tablewidget31(self, r):
        """
        计算账单详单到tablewidget31
        :param r: 账单详单
        """
        row_count = self.tablewidget31.rowCount()
        self.tablewidget31.setRowCount(row_count + 1)
        self.tablewidget31.setItem(row_count, 0, QTableWidgetItem(str(r.RoomNo)))
        self.tablewidget31.setItem(row_count, 1, QTableWidgetItem(
            r.connect_time[0].strftime("%Y-%m-%d %H:%M:%S")))
        self.tablewidget31.setItem(row_count, 2, QTableWidgetItem(str(r.disconnect_time)))
        self.tablewidget31.setItem(row_count, 3, QTableWidgetItem(str(round(r.total[0], 2))))
        self.tablewidget31.setItem(row_count, 4, QTableWidgetItem(str(round(r.total[1], 3))))

    def read_queue(self, tablewidget, q, string):
        """
        界面上显示两个队列信息
        :param tablewidget:
        :param q:
        :param string:
        """
        tablewidget.clearContents()  # 清屏
        for i in range(0, len(q)):
            tablewidget.setItem(0, i, QTableWidgetItem(str(q[i]['roomID'])))
            tablewidget.setItem(1, i, QTableWidgetItem(self.speed_num_to_str(q[i]['speed'])))
            tablewidget.setItem(2, i, QTableWidgetItem(str(q[i][string])))

    @staticmethod
    def speed_num_to_str(speed_num):
        """

        :param speed_num: 代表风速的数字(从1开始)
        :return: 风速的字符
        """
        speed_show = {1: "low", 2: "mid", 3: "high"}
        return speed_show[speed_num]

    def setParemeter(self):
        """
        设置服务器工作参数，发送给所有的客户端（之后还需要接入其它服务器设置）
        """
        QMessageBox.about(self, '设置成功', '工作模式：' + self.setParemeter_state() +
                          " 设置温度：" + str(self.sp.value()) + "°C")
        self.udpConnect.udp_sendall(str('#' + ' ' + self.setParemeter_state() + ' '
                                        + str(self.sp.value())))

    def setParemeter_state(self):
        """

        :return: 返回现在的state
        """
        r = ''
        if self.radioButton1.isChecked():
            r = "cool"
        if self.radioButton2.isChecked():
            r = "warm"
        return r

    def sendParemeter(self):
        """
        在一台客户端接入时，发送设置信息
        """
        self.udpConnect.udp_send(str('#' + ' ' + self.setParemeter_state()
                                     + ' ' + str(self.sp.value())))

    def startServer(self):
        """
        开启服务器
        """
        if self.udpConnect.udp_server_listen_start(self.connectNumberLineEdit.text()):
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)

    def closeServer(self):
        """
        关闭服务器
        """
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        print("before send bye")
        self.udpConnect.udp_sendall('bye')
        print("send bye finish")
        self.udpConnect.udp_server_close()

    def beginTest(self):
        """
        自动记录数值
        """
        output = open(self.get_beginTest_filename(), 'w+', encoding='gbk')
        self.beginTest_write_table(output)
        output.close()
        print('********* FINISH TEST *********')

    @staticmethod
    def get_beginTest_filename():
        """

        :return: 依据现在时间生成一个.xls文件
        """
        return './result/' + str(time.time()) + '.xls'

    def beginTest_write_table(self, output):
        """
        将table写入output
        :param output:
        :param table:
        """
        table = self.get_beginTest_table()
        output.write(
            '时间\t状态\t当前\t目标\t风速\t费用\t状态\t当前\t目标\t风速\t费用\t状态'
            '\t当前\t目标\t风速\t费用\t状态\t当前\t目标\t风速\t费用\t状态\t当前\t目标\t风速\t费用\n')
        for i in range(len(table)):
            output.write(str(i) + '\t')
            for j in range(len(table[i])):
                output.write(str(table[i][j]))
                output.write('\t')
            output.write('\n')  # 写完一行立马换行

    def get_beginTest_table(self):
        """
        :return: 返回table
        """
        r = []
        time.sleep(self.get_table_sleeptime())  # 错后一个周期
        for times in range(26):
            row = []
            for i in range(5):
                time.sleep(0.1)  # 保证(顺序获取结果）
                for j in range(5):
                    row.append(self.tablewidget1.item(i, j + 1).text())
            r.append(row)
            time.sleep(self.get_table_sleeptime() - 0.5)
        return r

    @staticmethod
    def get_table_sleeptime():
        """
        :return: 暂停的时长
        """
        return int(60 / int(ReadConfig.Config.getDispatch()['speed']))

    def write_msg(self, msg):
        """
        显示客户端接受信息，并且分析作出相应动作
        :param msg:
        """
        self.messageTextEdit.setText(msg)  # 首先将msg显示在状态栏上面
        self.log.insert_log(msg)  # 写日志到数据库（写主机接收到的消息
        if '?' in msg:
            self.write_wind_msg(msg)
        if '#' in msg:
            self.write_temperature_msg(msg)
        if "*" in msg:
            self.write_on_off_msg(msg)

    def write_wind_msg(self, msg):
        """
        将送风请求写入
        :param msg:
        """
        str2 = msg.split(' ')
        if int(str2[6]) == 0:
            self.write_stop_wind_msg(int(str2[5]))
        else:
            self.write_start_wind_msg(int(str2[5]), int(str2[6]))

    def write_start_wind_msg(self, room, speed):
        """
        开始送风请求，进入队列
        :param room: 房间号
        :param speed: 风速
        """
        stoproom, stopspeed, startroom, startspeed = self.dispatch.requestWind(room, speed)
        if stoproom > 0 and startroom > 0:
            self.write_start_wind_when_room_lack(startroom, startspeed, stoproom, stopspeed)
        elif stoproom > 0 and startroom == 0:
            self.write_start_wind_when_no_room(stoproom, stopspeed)
        elif stoproom == 0 and startroom > 0:
            self.write_start_wind_when_room_enough(startroom, startspeed)

    def write_start_wind_when_room_enough(self, startroom, startspeed):
        """
        服务队列未满，直接将新请求放入服务队列
        :param startroom:
        :param startspeed:
        """
        self.udpConnect.address = self.udpConnect.connectClient[str(startroom)]
        self.udpConnect.udp_send(self.get_wind_msg_str(startroom, startspeed))
        self.log.insert_log(self.get_wind_msg_str(startroom, startspeed))

    def write_start_wind_when_no_room(self, stoproom, stopspeed):
        """
        拒绝新请求，放入等待队列
        :param stoproom:
        :param stopspeed:
        """
        self.udpConnect.address = self.udpConnect.connectClient[str(stoproom)]
        self.udpConnect.udp_send(self.get_wind_msg_str(stoproom, stopspeed))
        self.log.insert_log(self.get_wind_msg_str(stoproom, stopspeed))  # 写日志到数据库

    def write_start_wind_when_room_lack(self, startroom, startspeed, stoproom, stopspeed):
        """
        服务队列满，但接收请求，原服务队列中的一个放入等待队列，新请求放入服务队列
        :param startroom:
        :param startspeed:
        :param stoproom:
        :param stopspeed:
        """
        self.udpConnect.address = self.udpConnect.connectClient[str(stoproom)]
        self.udpConnect.udp_send(self.get_wind_msg_str(stoproom, stopspeed))
        self.udpConnect.address = self.udpConnect.connectClient[str(startroom)]
        self.udpConnect.udp_send(self.get_wind_msg_str(startroom, startspeed))
        self.log.insert_log(self.get_wind_msg_str(startroom, startspeed))
        self.log.insert_log(self.get_wind_msg_str(stoproom, stopspeed))

    def write_stop_wind_msg(self, room):
        """
        停止送风请求，出队列
        :param room: 房间号
        """
        stoproom, stopspeed, startroom, startspeed = self.dispatch.stopWind(room)
        self.udpConnect.address = self.udpConnect.connectClient[str(stoproom)]
        self.udpConnect.udp_send(self.get_wind_msg_str(stoproom, stopspeed))
        self.log.insert_log(self.get_wind_msg_str(stoproom, stopspeed))  # 写日志到数据库
        if startroom > 0:  # 有房间要开始送风
            self.udpConnect.address = self.udpConnect.connectClient[str(startroom)]
            self.udpConnect.udp_send(self.get_wind_msg_str(startroom, startspeed))
            self.log.insert_log(self.get_wind_msg_str(startroom, startspeed))

    @staticmethod
    def get_wind_msg_str(stoproom, stopspeed):
        """

        :param stoproom: 房间号
        :param stopspeed: 风速
        :return: 整合风速停止的字符串
        """
        return "! " + str(stoproom) + ' ' + str(stopspeed)

    def closeEvent(self, event):
        """
        鼠标点击关闭动作
        :param event:
        """
        if self.get_close_reply() == QMessageBox.Yes:
            self.event_close_yes(event)
        else:
            event.ignore()

    def event_close_yes(self, event):
        """
        关闭该事件
        :param event:
        """
        event.accept()
        try:
            StopThreading.stop_thread(self.updateQueue_th)
        except ValueError:
            print("invalid thread id")
        self.udpConnect.udp_sendall('* bye')
        self.udpConnect.udp_server_close()

    def get_close_reply(self):
        """

        :return: 返回是否关闭
        """
        return QMessageBox.question(
            self,
            'Message',
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

    def dispatchRenew(self):
        """
        重启
        """
        if len(self.dispatch.queueW) != 0 and self.get_dispatch_stop_room() != 0:
            self.write_temperature_msg_when_queue()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec_())
