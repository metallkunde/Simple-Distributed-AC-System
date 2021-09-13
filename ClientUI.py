import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pic


class ClientWindow(QMainWindow):
    # 信号槽机制：设置一个信号，用于触发接收区写入动作
    signal_write_msg = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        palette1 = QPalette()
        palette1.setColor(palette1.Background, QColor(255, 255, 255))
        self.setPalette(palette1)  # 白色背景
        self.signal_write_msg.connect(self.write_msg)
        self.initUI()

    def box_beautify(self, box, filepath):  # 界面箱式布局美化
        string = open(filepath).read().strip('\n')
        box.setStyleSheet(string)

    def initUI(self):
        self.setWindowTitle('317B分布式温控系统客户端')
        self.setWindowIcon(QIcon(':ico_client.png'))
        self.resize(600, 400)

        # 整体模块
        sumlayout = QVBoxLayout()
        upLayout = QHBoxLayout()  # 日志
        downLayout = QVBoxLayout()  # 下面写别的

        # 1 日志文件******************************
        self.loglabel = QLabel('日志信息')
        self.udpLineEdit = QLineEdit()
        self.udpLineEdit.setStyleSheet('''
            QLineEdit{
                border:1px solid gray;
                border-radius:10px;}
        ''')
        self.udpLineEdit.setFocusPolicy(Qt.NoFocus)  # 设置不可编辑
        upLayout.addWidget(self.loglabel)
        upLayout.addWidget(self.udpLineEdit)

        # 底下是Tab
        hboxLayoutDown = QHBoxLayout()
        self.tabs = QTabWidget()  # 选项卡
        self.tab1 = QWidget()  # 子选项
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tabs.addTab(self.tab1, "服务器连接")
        self.tabs.addTab(self.tab2, "从机状态")
        self.tabs.addTab(self.tab3, "温度设置")
        self.tabs.addTab(self.tab4, "账单查询")
        hboxLayoutDown.addWidget(self.tabs)

        # 界面箱式布局美化
        #self.box_beautify(self.tab1, 'qss/connectBox.qss')
        #self.box_beautify(self.tab2, 'qss/state_bill_Box.qss')
        #self.box_beautify(self.tab3, 'qss/setBox.qss')
        #self.box_beautify(self.tab4, 'qss/state_bill_Box.qss')


        # 2 状态显示
        hboxLayout2 = QVBoxLayout()
        self.speedstateLabel = QLabel('风速:mid')
        self.stateLabel = QLabel('模式:cool')
        littlevboxLayout = QHBoxLayout()
        littlevboxLayout.addWidget(self.speedstateLabel)
        littlevboxLayout.addWidget(self.stateLabel)
        self.tempLcd = QLCDNumber()
        temp = 0.0
        temp = ("%.1f" % temp)
        self.tempLcd.display(temp)
        hboxLayout2.addLayout(littlevboxLayout)
        hboxLayout2.addWidget(self.tempLcd)
        hboxLayout2.setStretch(0, 1)
        hboxLayout2.setStretch(1, 2)
        self.tab2.setLayout(hboxLayout2)

        # 3 状态设定
        hboxLayout3 = QHBoxLayout()
        vboxLayout31 = QVBoxLayout()
        self.speedLable = QLabel('风速')
        self.radio1 = QRadioButton('高')
        self.radio2 = QRadioButton('中')
        self.radio3 = QRadioButton('低')
        self.radio2.setChecked(True)

        vboxLayout31.addWidget(self.radio1)
        vboxLayout31.addWidget(self.radio2)
        vboxLayout31.addWidget(self.radio3)
        hboxLayout3.addWidget(self.speedLable)
        hboxLayout3.addLayout(vboxLayout31)

        vboxLayout4 = QVBoxLayout()
        self.tempLable = QLabel('温度')
        self.sp = QSpinBox()
        self.sp.setValue(25)
        self.sp.setMinimum(18)
        self.sp.setMaximum(30)
        self.sendSpeedTempButton = QPushButton('确定设置')
        self.sendSpeedTempButton.setEnabled(False)
        vboxLayout4.addWidget(self.tempLable)
        vboxLayout4.addWidget(self.sp)
        vboxLayout4.addWidget(self.sendSpeedTempButton)

        hboxLayout1 = QHBoxLayout()
        hboxLayout1.addLayout(hboxLayout3)
        hboxLayout1.addLayout(vboxLayout4)
        self.tab3.setLayout(hboxLayout1)

        # 4 房间号，开关机及连接*****
        hboxLayoutp5 = QHBoxLayout()
        self.roomlabel = QLabel('房间号：')
        self.roomlabel.setFixedSize(300,100)
        self.roomlabel.setObjectName("roomlabel")
        self.w_roomID=QLCDNumber()
        self.w_roomID.setFixedSize(100,100)
        self.w_roomID.setSegmentStyle(QLCDNumber.Flat)
        self.w_roomID.setDigitCount(1)

        # self.w_roomID.setFocusPolicy(Qt.NoFocus)  # 设置界面上不可修改
        hboxLayoutp5.addWidget(self.roomlabel)
        hboxLayoutp5.addWidget(self.w_roomID)


        hboxLayout5 = QHBoxLayout()
        vboxLayoutLeft = QVBoxLayout()
        vboxLayoutRight = QVBoxLayout()

        self.ipLable = QLabel('服务器IP:')
        self.ipLineEdit = QLineEdit()
        self.ipLineEdit.setInputMask('000.000.000.000; ')
        vboxLayoutLeft.addWidget(self.ipLable)
        vboxLayoutRight.addWidget(self.ipLineEdit)

        # hboxLayout5.addWidget(self.ipLable)
        # hboxLayout5.addWidget(self.ipLineEdit)
        # hboxLayout5.setStretch(0, 1)
        # hboxLayout5.setStretch(1, 2)

        # hboxLayout6 = QHBoxLayout()
        self.portLable = QLabel('主机端口号:')
        # self.portLineEdit = QLineEdit()
        # self.portLineEdit.setMaxLength(4)
        self.portLineEdit = QSpinBox()
        self.portLineEdit.setRange(0,9999)
        self.connectButton = QPushButton('连接')
        self.connectButton.setCheckable(True)  # 可以复选

        vboxLayoutLeft.addWidget(self.portLable)
        vboxLayoutRight.addWidget(self.portLineEdit)

        hboxLayout5.addLayout(vboxLayoutLeft)
        hboxLayout5.addLayout(vboxLayoutRight)

        # hboxLayout6.addWidget(self.portLable)
        # hboxLayout6.addWidget(self.portLineEdit)
        # hboxLayout6.addWidget(self.connectButton)

        hboxLayout7 = QHBoxLayout()
        self.openButton = QPushButton('开机')
        self.closeButton = QPushButton('关机')
        self.openButton.setEnabled(False)
        self.closeButton.setEnabled(False)
        hboxLayout7.addWidget(self.connectButton)
        hboxLayout7.addWidget(self.openButton)
        hboxLayout7.addWidget(self.closeButton)


        vboxLayout2 = QVBoxLayout()
        vboxLayout2.addLayout(hboxLayoutp5)
        vboxLayout2.addLayout(hboxLayout5)
        # vboxLayout2.addLayout(hboxLayout6)
        vboxLayout2.addLayout(hboxLayout7)
        self.tab1.setLayout(vboxLayout2)

        # 5 消费金额
        vboxLayout8 = QVBoxLayout()
        curr_bill = QLabel('当前消费金额：')
        curr_bill.setFixedSize(self.width(),50)
        # self.bill = QLineEdit()
        self.bill=QLCDNumber()
        vboxLayout8.addWidget(curr_bill)
        vboxLayout8.addWidget(self.bill)
        self.tab4.setLayout(vboxLayout8)


        # 各部分载入
        downLayout.addLayout(hboxLayoutDown)
        sumlayout.addLayout(downLayout)
        sumlayout.addLayout(upLayout)

        centerWidget = QWidget()
        centerWidget.setLayout(sumlayout)
        self.setCentralWidget(centerWidget)

    def write_msg(self, msg):
        self.udpLineEdit.setText(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    client = ClientWindow()
    client.show()

    sys.exit(app.exec_())
