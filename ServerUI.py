
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import datetime


class ServerWindow(QWidget):
    # 信号槽机制：设置一个信号，用于触发接收区写入动作
    signal_write_msg = pyqtSignal(str)

    def __init__(self):
        super(ServerWindow, self).__init__()
        self.signal_write_msg.connect(self.write_msg)
        self.initUI()

    def show_statement(self, tablewidget2x, tab2x, hboxLayoutRight21x):  # 将报表显示在界面
        tablewidget2x.horizontalHeader().setCascadingSectionResizes(True)
        tab2x.layout.addItem(hboxLayoutRight21x)
        tab2x.layout.addWidget(tablewidget2x)
        tab2x.setLayout(tab2x.layout)

    def box_beautify(self, box, filepath):  # 界面箱式布局美化
        string = open(filepath).read().strip('\n')
        box.setStyleSheet(string)

    def show_queue(self, tablewidget, hl_str):  # 两个队列设置
        tablewidget.setRowCount(3)
        tablewidget.setColumnCount(10)
        tablewidget.horizontalHeader().setVisible(False)
        tablewidget.setVerticalHeaderLabels(['房间号', '风速', hl_str])

    def table_settings(self, tablewidget3x, row, column, str_list, c_start):  # 各选项卡里表格设置
        tablewidget3x.setRowCount(row)
        tablewidget3x.setColumnCount(column)
        tablewidget3x.verticalHeader().setVisible(False)
        tablewidget3x.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tablewidget3x.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(c_start, column):
            tablewidget3x.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        tablewidget3x.setHorizontalHeaderLabels(str_list)

    def initUI(self):
        self.setWindowTitle('分布式空调管理系统')
        self.setWindowIcon(QIcon(':ico_server.png'))
        palette1 = QPalette()
        palette1.setColor(palette1.Background, QColor(255, 255, 255))
        self.setPalette(palette1)  # 白色背景
        self.resize(400, 400)
        # 整体布局
        self.leftUpLayout = QVBoxLayout()
        self.leftDownLayout = QVBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.sumlayout = QHBoxLayout()

        self.leftupBox = QGroupBox('空调机设置')
        self.leftdownBox = QGroupBox('服务器设置')
        self.rightBox = QGroupBox('系统及报表账单')

        # 界面箱式布局美化
        #self.box_beautify(self.leftupBox, 'qss/leftupBox.qss')
        #self.box_beautify(self.leftdownBox, 'qss/leftdownBox.qss')
        #self.box_beautify(self.rightBox, 'qss/rightBox.qss')

        hboxLayoutDown = QHBoxLayout()
        self.tab0s = QTabWidget()  # 选项卡
        self.tab01 = QWidget()  # 子选项
        self.tab02 = QWidget()
        self.tab03 = QWidget()

        self.tab0s.addTab(self.tab01, "空调机设置")
        self.tab0s.addTab(self.tab02, "服务器设置")
        self.tab0s.addTab(self.tab03, "系统及报表账单")
        hboxLayoutDown.addWidget(self.tab0s)
        self.sumlayout.addLayout(hboxLayoutDown)

        # 左侧界面
        # 空调机设置
        hboxLayoutLeft1 = QHBoxLayout()
        label1 = QLabel('工作方式：')

        self.radioButton1 = QRadioButton('制冷')
        self.radioButton2 = QRadioButton('制热')
        self.radioButton1.setChecked(True)

        hboxLayoutLeft1.addWidget(label1)
        hboxLayoutLeft1.addWidget(self.radioButton1)
        hboxLayoutLeft1.addWidget(self.radioButton2)

        hboxLayoutLeft2 = QHBoxLayout()
        QLabel2 = QLabel('默认温度：')

        self.sp = QSpinBox()
        self.sp.setValue(25)
        self.sp.setMinimum(17)
        self.sp.setMaximum(26)

        self.setButton = QPushButton('确定')

        hboxLayoutLeft2.addWidget(QLabel2)
        hboxLayoutLeft2.addWidget(self.sp)
        hboxLayoutLeft2.addWidget(self.setButton)

        # 服务器设置
        hboxLayoutLeft3 = QHBoxLayout()
        self.ipLabel = QLabel('IP:')
        self.ipLabel.setMaximumSize(70, 40)
        self.ipLineEdit = QLineEdit()
        self.getipButton = QPushButton('获取')

        hboxLayoutLeft3.addWidget(self.ipLabel)
        hboxLayoutLeft3.addWidget(self.ipLineEdit)
        hboxLayoutLeft3.addWidget(self.getipButton)

        hboxLayoutLeft4 = QHBoxLayout()
        self.connectPortLabel = QLabel("服务器端口设置:")
        self.connectNumberLineEdit = QLineEdit("2222")

        hboxLayoutLeft4.addWidget(self.connectPortLabel)
        hboxLayoutLeft4.addWidget(self.connectNumberLineEdit)

        hboxLayoutLeft5 = QHBoxLayout()
        self.startButton = QPushButton('开机')
        self.stopButton = QPushButton('关机')
        self.stopButton.setEnabled(False)
        hboxLayoutLeft5.addWidget(self.startButton)
        hboxLayoutLeft5.addWidget(self.stopButton)

        # 右侧界面
        hboxLayoutRight1 = QHBoxLayout()
        self.tabs = QTabWidget()  # 选项卡
        self.tab1 = QWidget()  # 子选项
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tabs.addTab(self.tab1, "空调运行状态")
        self.tabs.addTab(self.tab2, "查询报表")
        self.tabs.addTab(self.tab3, "生成账单")
        self.tabs.addTab(self.tab4, "服务和等待队列")
        hboxLayoutRight1.addWidget(self.tabs)

        # 选项卡1:监控信息
        self.messageTextEdit = QLineEdit()
        self.messageTextEdit.setFocusPolicy(Qt.NoFocus)  # 设置不可编辑
        self.messageLabel = QLabel('日志信息')

        hboxLayoutRight11 = QHBoxLayout()
        hboxLayoutRight11.addWidget(self.messageLabel)
        hboxLayoutRight11.addWidget(self.messageTextEdit)

        self.tablewidget1 = QTableWidget()
        str_list = ['房间号', '状态', '当前温度', '设定温度', '设定风速', '当前费用']
        self.table_settings(self.tablewidget1, 10, 6, str_list, 6)
        for i in range(10):
            self.tablewidget1.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tablewidget1.setItem(i, 1, QTableWidgetItem('disconnected'))
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addItem(hboxLayoutRight11)
        self.tab1.layout.addWidget(self.tablewidget1)
        self.tab1.setLayout(self.tab1.layout)

        # 选项卡2：报表
        self.tabs_2 = QTabWidget()
        self.tab21 = QWidget()
        self.tab22 = QWidget()
        self.tab23 = QWidget()
        self.tab24 = QWidget()
        self.tabs_2.addTab(self.tab21, "日报表")
        self.tabs_2.addTab(self.tab22, "周报表")
        self.tabs_2.addTab(self.tab23, "月报表")
        self.tabs_2.addTab(self.tab24, "年报表")

        hboxLayoutRight211 = QHBoxLayout()
        hboxLayoutRight212 = QHBoxLayout()
        hboxLayoutRight213 = QHBoxLayout()
        hboxLayoutRight214 = QHBoxLayout()
        hboxLayoutRight22 = QHBoxLayout()

        # 日报表
        timeLabel = QLabel('选择日期：  ')
        self.datetimeEdit21 = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetimeEdit21.setDisplayFormat("yyyy/MM/dd")

        self.setDayButton = QPushButton('确认')
        hboxLayoutRight211.addWidget(timeLabel)
        hboxLayoutRight211.addWidget(self.datetimeEdit21)
        hboxLayoutRight211.addWidget(self.setDayButton)

        self.tablewidget21 = QTableWidget()
        str_list = ['房间号', '使用次数', '常用温度', '常用风速', '达到目标次数', '调度次数', '详单数', '消费金额']
        self.table_settings(self.tablewidget21, 10, 8, str_list, 5)

        # 周报表
        timeLabel = QLabel('选择本年度周次：  ')
        self.week = QSpinBox()
        t = datetime.datetime.now().isocalendar()  # (2020, 16, 7)当前年[0]，当前周[1],当前周的第几天[2]
        week_count = t[1]
        self.week.setValue(week_count)
        self.week.setMinimum(1)
        self.week.setMaximum(52)

        self.setWeekButton = QPushButton('确认')
        hboxLayoutRight212.addWidget(timeLabel)
        hboxLayoutRight212.addWidget(self.week)
        hboxLayoutRight212.addWidget(self.setWeekButton)

        self.tablewidget22 = QTableWidget()
        self.table_settings(self.tablewidget22, 10, 8, str_list, 5)

        # 月报表
        timeLabel = QLabel('选择本年度月份：  ')
        self.datetimeEdit22 = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetimeEdit22.setDisplayFormat("MM")

        self.setMonButton = QPushButton('确认')
        hboxLayoutRight213.addWidget(timeLabel)
        hboxLayoutRight213.addWidget(self.datetimeEdit22)
        hboxLayoutRight213.addWidget(self.setMonButton)

        self.tablewidget23 = QTableWidget()
        self.table_settings(self.tablewidget23, 10, 8, str_list, 5)

        # 年报表
        timeLabel = QLabel('选择年份：  ')
        self.datetimeEdit23 = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetimeEdit23.setDisplayFormat("yyyy")

        self.setYearButton = QPushButton('确认')
        hboxLayoutRight214.addWidget(timeLabel)
        hboxLayoutRight214.addWidget(self.datetimeEdit23)
        hboxLayoutRight214.addWidget(self.setYearButton)

        self.tablewidget24 = QTableWidget()
        self.table_settings(self.tablewidget24, 10, 8, str_list, 5)

        # 所有报表公用的费用和用电量
        total_bill = QLabel('  总费用  ')
        total_elec = QLabel('  总用电量  ')
        self.bill2 = QLineEdit()
        self.bill2.setFocusPolicy(Qt.NoFocus)  # 设置不可编辑
        self.electricity2 = QLineEdit()
        self.electricity2.setFocusPolicy(Qt.NoFocus)  # 设置不可编辑

        hboxLayoutRight22.addWidget(total_bill)
        hboxLayoutRight22.addWidget(self.bill2)
        hboxLayoutRight22.addWidget(total_elec)
        hboxLayoutRight22.addWidget(self.electricity2)
        # 在选项卡显示各报表
        # 日报表
        self.tab21.layout = QVBoxLayout(self)
        self.show_statement(self.tablewidget21, self.tab21, hboxLayoutRight211)
        # 周报表
        self.tab22.layout = QVBoxLayout(self)
        self.show_statement(self.tablewidget22, self.tab22, hboxLayoutRight212)
        # 月报表
        self.tab23.layout = QVBoxLayout(self)
        self.show_statement(self.tablewidget23, self.tab23, hboxLayoutRight213)
        # 年报表
        self.tab24.layout = QVBoxLayout(self)
        self.show_statement(self.tablewidget24, self.tab24, hboxLayoutRight214)

        # 总报表
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.addWidget(self.tabs_2)
        self.tab2.layout.addItem(hboxLayoutRight22)
        self.tab2.setLayout(self.tab2.layout)

        # 选项卡3：详单
        self.tabs_3 = QTabWidget()
        self.tab31 = QWidget()
        self.tab32 = QWidget()
        self.tabs_3.addTab(self.tab31, "概览")
        self.tabs_3.addTab(self.tab32, "详情")
        hboxLayoutRight31 = QHBoxLayout()
        hboxLayoutRight32 = QHBoxLayout()

        # 概览
        self.billOutButton = QPushButton('导出账单')
        self.billOutButton.setMaximumSize(120, 50)
        self.tablewidget31 = QTableWidget()
        str_list = ['房间号', '入住时间', '离店时间', '消费金额', '耗电量']
        self.table_settings(self.tablewidget31, 0, 5, str_list, 3)
        self.tablewidget31.horizontalHeader().setCascadingSectionResizes(True)

        # 详情
        bill_label = QLabel('最新生成账单详情：')
        hboxLayoutRight31.addWidget(bill_label)

        self.tablewidget32 = QTableWidget()
        str_list = ['房间号', '开始送风时间', '结束送风时间', '送风时长', '风速', '费率', '费用']
        self.table_settings(self.tablewidget32, 0, 7, str_list, 3)

        detail_bill = QLabel('总金额')
        self.de_b_Text = QLineEdit()
        self.de_b_Text.setFocusPolicy(Qt.NoFocus)  # 设置不可编辑
        detail_elec = QLabel('总用电')
        self.de_e_Text = QLineEdit()
        self.de_e_Text.setFocusPolicy(Qt.NoFocus)  # 设置不可编辑
        hboxLayoutRight32.addWidget(detail_bill)
        hboxLayoutRight32.addWidget(self.de_b_Text)
        hboxLayoutRight32.addWidget(detail_elec)
        hboxLayoutRight32.addWidget(self.de_e_Text)
        hboxLayoutRight32.setSpacing(30)

        # 概览
        self.tab31.layout = QVBoxLayout(self)
        self.tab31.layout.addWidget(self.tablewidget31)
        self.tab31.layout.addWidget(self.billOutButton)
        self.tab31.setLayout(self.tab31.layout)
        # 详情
        self.tab32.layout = QVBoxLayout(self)
        self.tab32.layout.addItem(hboxLayoutRight31)
        self.tab32.layout.addWidget(self.tablewidget32)
        self.tab32.layout.addItem(hboxLayoutRight32)
        self.tab32.setLayout(self.tab32.layout)

        # 详单（总）
        self.tab3.layout = QVBoxLayout(self)
        self.tab3.layout.addWidget(self.tabs_3)
        self.tab3.setLayout(self.tab3.layout)

        # 选项卡4：服务和等待队列
        serve_label = QLabel('服务队列')
        self.tablewidget4 = QTableWidget()
        self.show_queue(self.tablewidget4, '服务时间')
        wait_label = QLabel('等待队列')
        self.tablewidget5 = QTableWidget()
        self.show_queue(self.tablewidget5, '等待时间')

        self.tab4.layout = QVBoxLayout(self)
        self.tab4.layout.addWidget(serve_label)
        self.tab4.layout.addWidget(self.tablewidget4)
        self.tab4.layout.addWidget(wait_label)
        self.tab4.layout.addWidget(self.tablewidget5)
        self.tab4.setLayout(self.tab4.layout)

        # 整体布局
        self.leftUpLayout.addLayout(hboxLayoutLeft1)
        self.leftUpLayout.addLayout(hboxLayoutLeft2)
        #self.leftupBox.setLayout(self.leftUpLayout)
        self.tab01.setLayout(self.leftUpLayout)

        self.leftDownLayout.addLayout(hboxLayoutLeft3)
        self.leftDownLayout.addLayout(hboxLayoutLeft4)
        self.leftDownLayout.addLayout(hboxLayoutLeft5)
        #self.leftdownBox.setLayout(self.leftDownLayout)
        self.tab02.setLayout(self.leftDownLayout)

        self.rightLayout.addLayout(hboxLayoutRight1)
        self.rightBox.setLayout(self.rightLayout)
        self.tab03.setLayout(self.rightLayout)

        self.leftLayout.addWidget(self.leftupBox)
        self.leftLayout.addWidget(self.leftdownBox)

        #self.sumlayout.addLayout(self.leftLayout)
        #self.sumlayout.addWidget(self.rightBox)
        self.sumlayout.setStretch(0, 1)
        self.sumlayout.setStretch(1, 2)
        self.setLayout(self.sumlayout)

    def write_msg(self, msg):
        self.messageTextEdit.setText(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 登录窗口
    window = ServerWindow()
    window.show()

    sys.exit(app.exec_())
