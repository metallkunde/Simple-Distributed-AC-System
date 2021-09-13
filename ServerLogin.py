#coding=utf-8
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from ServerMain import *
import pic


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.loginBtn.clicked.connect(self.loginIn)
        self.cancerBtn.clicked.connect(self.close)

    def initUI(self):
        palette1 = QPalette()
        palette1.setColor(palette1.Background, QColor(255, 255, 255))
        self.setPalette(palette1)  # Cornislk
        string = open("qss/Login.qss", encoding='utf-8').read().strip('\n')
        self.setStyleSheet(string)
        layout = QVBoxLayout()
        self.imagelable = QLabel("显示图片")
        self.imagelable.setPixmap(QPixmap("./image/serverlogin.jpg"))

        Hlayout1 = QHBoxLayout()
        self.pwdLabel = QLabel('密码：')
        self.pwdLineEdit = QLineEdit()
        self.pwdLineEdit.setEchoMode(QLineEdit.Password)
        self.pwdLineEdit.setText("admin")
        Hlayout1.addWidget(self.pwdLabel)
        Hlayout1.addWidget(self.pwdLineEdit)

        Hlayout2 = QHBoxLayout()
        self.loginBtn = QPushButton('登录')
        self.cancerBtn = QPushButton('退出')
        self.loginBtn.setFixedSize(50, 50)
        self.cancerBtn.setFixedSize(50, 50)
        Hlayout2.addWidget(self.loginBtn)
        Hlayout2.addWidget(self.cancerBtn)

        layout.addWidget(self.imagelable)
        layout.addLayout(Hlayout1)
        layout.addLayout(Hlayout2)

        self.setLayout(layout)
        self.setWindowTitle('登录空调管理系统')

    def loginIn(self):
        if self.pwdLineEdit.text() == 'admin':
            self.hide()
            self.mainWindow = Main()
            self.mainWindow.show()
        else:
            QMessageBox.critical(self, '密码错误', '请重新输入密码')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 加载界面
    #pixmap = QPixmap("/image/loading.jpg")
    #pixmap.scaled(200, 150, aspectRatioMode=Qt.IgnoreAspectRatio, transformMode=Qt.FastTransformation)
    #splash = QSplashScreen(pixmap)
    #splash.show()
    #splash.showMessage(u'Loading...', alignment=Qt.AlignBottom, color=Qt.white)
    time.sleep(1)

    # 登录窗口
    windowFirst = LoginWindow()
    windowFirst.show()

    # 窗口加载完成后关闭画面
    #splash.finish(windowFirst)
    sys.exit(app.exec_())
