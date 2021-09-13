from PyQt5.QtGui import *
from ClientMain import *

SKY_BLUE = QColor(135,206,235)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.roomID = 1
        self.initUI()
        self.loginBtn.clicked.connect(self.loginIn)
        self.cancerBtn.clicked.connect(self.close)

    def initUI(self):
        palette1 = QPalette()
        palette1.setColor(palette1.Background, SKY_BLUE)
        self.setPalette(palette1)
        string = open("qss/Login.qss", encoding='UTF-8').read().strip('\n')
        self.setStyleSheet(string)
        layout = QVBoxLayout()
        self.imagelable = QLabel("显示图片")
        self.imagelable.setPixmap(QPixmap("./image/air_con.jpg"))


        Hlayout1 = QHBoxLayout()
        self.pwdLabel = QLabel('选择您的房间号码(1~9)：')
        self.roomSpinBox = QSpinBox()
        self.roomSpinBox.setRange(1,9)
        self.roomSpinBox.setSingleStep(1)
        self.roomSpinBox.setValue(1)
        Hlayout2 = QHBoxLayout()
        Vlayout1 = QVBoxLayout()
        Vlayout2 = QVBoxLayout()

        Vlayout1.addWidget(self.pwdLabel)
        Vlayout1.addWidget(self.roomSpinBox)

        self.loginBtn = QPushButton('确认')
        self.cancerBtn = QPushButton('取消')

        self.loginBtn.setFixedSize(200,50)
        self.cancerBtn.setFixedSize(200,50)

        Vlayout2.addWidget(self.loginBtn)
        Vlayout2.addWidget(self.cancerBtn)

        layout.addWidget(self.imagelable)
        layout.addLayout(Hlayout1)
        layout.addLayout(Hlayout2)
        Hlayout2.addLayout(Vlayout1)
        Hlayout2.addLayout(Vlayout2)

        self.setLayout(layout)
        self.setWindowTitle('317B分布式温控系统客户端')

    def loginIn(self):
        if self.roomSpinBox.text().isdigit():
            self.roomID = int(self.roomSpinBox.text())
            self.hide()
            self.mainWindow = Main(self.roomID)
            self.mainWindow.show()
        else:
            QMessageBox.critical(self, '房间号错误', '请重新输入')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 登录窗口
    windowFirst = LoginWindow()
    windowFirst.show()

    sys.exit(app.exec_())
