import time


class Log():  # 日志类
    def __init__(self, mapper):
        # 每行有6位 [0]RoomNo,[1]state,[2]CurrentTemp,[3]TargetTemp,[4]WindSpeed,[5]money
        self.last_msg = []  # 二维list存储上一条信息，每行一个房间
        self.kwh_per_yuan = 1   # 一块钱几度电（按定义）kilowatt hour per yuan
        self.verbose = True     # 打印调试信息
        self.mapper = mapper

    def insert_log(self, msg):
        if '#' in msg:
            # 处理字符串消息
            str0 = msg.split('#')  # 切掉前面的 IP 192.168.35.1 PORT 62485 #
            str0 = str0[1].split(' ')
            str0 = str0[1:]
            # str0有6位 [0]RoomNo,[1]state,[2]CurrentTemp,[3]TargetTemp,[4]WindSpeed,[5]money
            str00 = str0[:]  # copy一份str0
            # 查找有无上一条数据
            for i in range(len(self.last_msg)):
                if self.last_msg[i][0] == str0[0]:  # 有(找到了房间号）
                    curr_money = str0[-1]
                    del str0[-1]
                    str0 = str0 + [str(float(curr_money) - float(self.last_msg[i][5]))]
                    break

            # 执行sql语句
            ret = self.mapper.insert(
                '''
                insert into log(RoomNo,state,CurrentTemp,TargetTemp,WindSpeed,money,PowerConsumption)
                values(%s,%s,%s,%s,%s,%s,%s)
                '''
                , params=str0 + [str(float(str0[5]) * self.kwh_per_yuan)])

            # 存储上一条信息
            for i in range(len(self.last_msg)):
                if (self.last_msg[i][0] == str00[0]):
                    self.last_msg[i] = str00
                    return
            self.last_msg.append(str00)  # 循环完毕没找到该房间的记录就新增一个房间
            # if (self.verbose): print("tui chu le")
            return

        # * 打头是开关连接控制 start 和 close
        if "*" in msg:
            str1 = msg.split('*')  # 切掉前面的 IP 192.168.35.1 PORT 62485 #
            str1 = str1[1].split(' ')
            str1 = str1[1:]
            # # 连接对象
            # sqlTool = SQLtool()
            # 执行sql语句
            ret = self.mapper.insert(
                '''
                insert into control(state,RoomNo)
                values(%s,%s)
                '''
                , params=str1)

            if str1[0]=='close':
                ret = self.mapper.insert( #还要额外写停止送风
                    '''
                    insert into windcontrol(RoomNo,WindSpeed,flag)
                    values(%s,0,1)
                    '''
                    , params=str1[1])
                # if (self.verbose):
                #     # print([str2][0] + [str(1)])
                #     if ret > 0:
                #         print('插入数据库成功')
                #     else:
                #         print('插入数据库失败', str1[1]+',0,1')
            return

        # 风速控制信息 ? 打头是客户端请求，！打头是主机回传
        if "?" in msg:
            str2 = msg.split('?')
            str2 = str2[1].split(' ')
            str2 = str2[1:]
            # # 连接对象
            # sqlTool = SQLtool()
            # 执行sql语句
            ret = self.mapper.insert(
                '''
                insert into windcontrol(RoomNo,WindSpeed,flag)
                values(%s,%s,%s)
                '''
                , params=[str2][0] + [str(0)])

            return

        # ！打头是主机回传
        if "!" in msg:
            str2 = msg.split('!')
            str2 = str2[1].split(' ')
            str2 = str2[1:]
            # # 连接对象
            # sqlTool = SQLtool()
            # 执行sql语句
            ret = self.mapper.insert(
                '''
                insert into windcontrol(RoomNo,WindSpeed,flag)
                values(%s,%s,%s)
                '''
                , params=[str2][0] + [str(1)])
            if self.verbose:
                # print([str2][0] + [str(1)])
                print("尝试插入数据库", msg)
                if ret > 0:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'插入数据库成功',msg)
                else:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'插入数据库失败',msg)
                    print('ret = ',msg)
            return

    def del_last_msg(self, RoomNo):  # 客户端断开连接时调用！
        # 查找有无上一条数据
        if self.verbose: print('尝试删除上一条数据 roomNo',RoomNo)
        for i in range(len(self.last_msg)):
            if self.last_msg[i][0] == RoomNo:  # 有(找到了房间号）
                self.last_msg.pop(i)
                if self.verbose: print('删除了断开连接的客户端数据')
                break


if __name__ == '__main__':
    test_log = Log()
    test_log.insert_log('# 1 close 25.0 19 high 0')
    test_log.insert_log('* start 1 13')
    test_log.insert_log('# 1 run 25.0 19 high 0.016666666666666666')

