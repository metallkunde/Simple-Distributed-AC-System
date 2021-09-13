#分布式温控系统软件使用说明
某快捷廉价酒店响应节能绿色环保理念，推行自助计费式中央温控系统，使得入住的客户可以根据要求设定温度和风速的调节，同时可以显示所需支付的金额。客户退房时酒店须出具空调使用的账单及详单。空调运行期间，空调管理员能够监控各房间空调的使用状态，此外，酒店经理在需要的情况下可以查看不同时间范围内的格式化统计报表。
##目录
###[配置](#1.配置)
###[项目说明](#2.项目说明)
###1.配置
####1.1 配置数据库
   打开config.ini  
   在[DATABASE]中修改密码为本机MySQL数据库登录信息

    user='root', passwd='你的密码' 
####1.2 在Pycharm中连接数据库  
   在Pycharm上方工具栏中选择：
    
    View—Tool Windows—Database
   新建数据库连接
    
    数据库名称：hotel_air_condition
    
   运行hotel_air_condition.sql文件  
   打开数据库Console可以方便在pycharm中进行查询
####1.3 调度控制模块
   打开config.ini  
   在[DISPATCH]中修改调度控制模块参数

    speed = 60 #  仿真速率
    quelen = 3 #  服务队列长度
    waittime = 120 #  最长等待时间
####1.4 温度控制器模块
   打开config.ini  
   在[TEMPCONTROL]中修改调度控制模块参数

    speed = 60 #  仿真速率
    refreshseq = 1
    highprice = 1 #  高风单位时间计费
    midprice = 0.5 #  中风
    lowprice = 0.3333 #  低风
    highdelta = 0.6 #  高风温度变化速率
    middelta = 0.5 # 中风
    lowdelta = 0.4 # 低风
####1.4 测试模块
   打开config.ini  
   设置[TEST]中flag决定是否开启测试模式
   
    flag = 0 #  1为开启，0为关闭，测试模式下运行5个客户端，自动执行程序
####1.5 各房间初始温度设置
   打开config.ini  
   在[BEGINTEMP]中按房间序号修改各个房间初始温度
###2.项目说明
####2.1 项目文件夹
    /data/bill/:存放导出账单xls文件
    /data/receipt/:存放详单
    /data/result/:存放测试模式的运行结果
    /data/input/:存放测试模式下的输入xls文件
    /source/image/:存放程序运行过程中界面需要用到的图片
    /source/qss/:存放所有界面的qss样式
    /source/:存放图片和qss两个文件夹以及数据库的sql文件、README.md、requirements.txt
    /newfile/:测试中用到的py文件
    /bin/:存放配置文件
####2.2 代码文件
    ClientLogin.py:用户登录界面，非测试模式下启动用户端
    ClientUI.py:用户使用空调界面前端
    ClientMain.py:用户使用空调后端
    ServerLogin.py:管理员登录界面，非测试模式下启动中央空调
    ServerUI.py：中央空调界面前端
    ServerMain.py:中央空调后端
    ServerDispatch.py:中央空调系统实现调度算法
    UDPClient.py:用户端的UDP通信
    UDPServer.py：中央空调的UDP通信
    TempControl.py:实现用户端空调温度控制
    StopThreading.py:用户线程的控制
    Database.py：向数据库中写入日志信息
    SQLTool.py:封装的数据库操作（登录和CURD）
    Statement.py:报表计算和产生
    Receipt.py:详单计算和产生
    ReadConfig.py:读取配置文件信息
    pic.py:生成的图片代码
####2.3 输入和输出
#####2.3.1 测试模式
通过input.xls自动输入，运行过程在result文件夹内文件输出
#####2.3.2 非测试模式
输入  
    ClientLogin:输入1为正整数作为房间号
    ServerLogin:输入密码作为登录依据，密码默认admin  
输出  
    运行过程在服务端和客户端的UI和控制台分别显示
####2.4 PyQt中显示图片流程
2.4.1 png图片放在image文件夹中  
2.4.2 再pic.qrc中添加一行 <file>image/login.png</file>4  
2.4.3 将其转成python代码 pyrcc5 pic.qrc -o pic.py  
2.4.4 需要使用图片的时候引用 import pic  
2.4.5 图片路径为 ":image/login.png"  
####2.5 pyinstall生成可执行文件指令
2.5.1 pyinstaller -F -w -i client_ico.ico ClientLogin.py  
2.5.2 pyinstaller -F -w -i server_ico.ico ServerLogin.py  

