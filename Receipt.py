from Mapper import Mapper
import time
from datetime import datetime,timedelta
import ReadConfig


class Receipt():
    def __init__(self, RoomNo):
        config = ReadConfig.Config.getTempcontrol()
        self.power_map = {0: 0, 1: float(config['lowprice']), 2: float(config['midprice']), 3: float(config['highprice'])}
        self.RoomNo = RoomNo  # 房间号
        self.row_cnt = 0  # 行数
        self.connect_time = ''  #
        self.disconnect_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.detail = []  # 详单
        self.total = []  # 统计总空调费和总用电量
        self.verbose = False
        self.id = time.strftime(RoomNo + "%Y%m%d%H%M", time.localtime())  # 详单id

    def getReceipt(self):  # 计算详单
        if self.verbose: print('try receipt')
        # 连接对象
        sqlTool = Mapper()

        # 算起止时间
        # 终止时间直接sql语句体现
        self.connect_time = sqlTool.select_one(  # 查起始时间
            '''
            select msgTime
            from control
            where roomNo=%s and state='hi'
            ORDER BY msgTime DESC
            LIMIT 1
            '''
            , params=self.RoomNo)

        # 查询详细数据
        wind_row_count, wind = sqlTool.select_all(  # 开机时间
            '''
            select WindSpeed,msgTime
            from windcontrol
            where roomNo=%s and msgTime>=%s and msgTime<=CURRENT_TIME() and flag=1
            ORDER BY msgTime ASC
            '''
            , params=[self.RoomNo, self.connect_time])

        # 0房间号、1开始送风时间、2结束送风时间、3送风时长、4风速、5费率、6费用
        wind_map = {0: '停止送风', 1: '低风', 2: '中风', 3: '高风'}
        # power_map = {0: 0, 1: 0.4, 2: 0.5, 3: 0.6}
        last_windspeed=0
        flag = 0
        rcp = [[]]
        self.row_cnt = 0
        for row in wind:
            if flag == 0: # 未送风
                if row[0] > 0:  # start
                    self.row_cnt += 1
                    rcp.append([self.RoomNo, row[1], 0, 0, wind_map[row[0]], self.power_map[row[0]], 0])
                    last_windspeed=row[0]
                    flag = 1

            elif flag == 1: # 正在送风
                if row[0] == 0:  # stop
                    rcp[self.row_cnt][2] = row[1]  # 结束送风时间
                    rcp[self.row_cnt][3] = rcp[self.row_cnt][2] - rcp[self.row_cnt][1]  # 送风时长
                    rcp[self.row_cnt][6] = rcp[self.row_cnt][3].seconds / 60 * rcp[self.row_cnt][5]
                    flag = 0
                    last_windspeed = row[0]

                elif row[0] > 0 and last_windspeed!=row[0]:  # 修改风速（并且不是发相同的控制信息
                    rcp[self.row_cnt][2] = row[1]  # 结束送风时间
                    rcp[self.row_cnt][3] = rcp[self.row_cnt][2] - rcp[self.row_cnt][1]  # 送风时长
                    rcp[self.row_cnt][6] = rcp[self.row_cnt][3].seconds / 60 * rcp[self.row_cnt][5]

                    self.row_cnt += 1
                    rcp.append([self.RoomNo, row[1], 0, 0, wind_map[row[0]], self.power_map[row[0]], 0])
                    flag = 1
                    last_windspeed = row[0]

        if flag == 1: # 最后没有发关机的控制信号
            rcp[self.row_cnt][2] = datetime.now()  # 结束送风时间
            rcp[self.row_cnt][3] = rcp[self.row_cnt][2] - rcp[self.row_cnt][1]  # 送风时长
            rcp[self.row_cnt][6] = rcp[self.row_cnt][3].seconds / 60 * rcp[self.row_cnt][5]
            flag = 0

        rcp.pop(0)
        self.detail = rcp
        if self.verbose:
            print(self.detail)

        # 统计总空调费和总用电量
        aggregate = sqlTool.select_one(
            '''
            select sum(money),sum(PowerConsumption) from log
             where RoomNo=%s and msgTime>=%s and msgTime<=CURRENT_TIME() 
            '''
            , params=[self.RoomNo, self.connect_time])

        self.total = aggregate

        # 写文件 文件名是‘房间号时间’ 时间格式是‘YYYYMMDDHHMMSS'
        f = open(file='./receipt/' + self.id + '.xls', mode="w")
        f.write('房间号\t开始送风时间\t结束送风时间\t送风时长\t风速\t费率\t费用\n')
        for row in rcp:
            for i in row:
                f.write(str(i)+'\t')
            f.write('\n')
            # f.write(str(row[0]) + '\t' + str(row[1]) + '\t' + str(row[2]) +
            #             #     '\t' + str(row[3]) + '\t' + str(row[4]) + '\t' + str(row[5]) + '\t' + str(
            #             #     round(row[6],2)) + '\n')
        f.write('\n总费用\t' + str(self.total[0]))
        t1 = [row[3] for row in rcp]
        total_time = sum(t1, timedelta())
        f.write('\n总时长\t' + str(total_time))
        f.close()

        # 写数据库
        sqlTool = Mapper()
        # 执行sql语句
        ret = sqlTool.insert(
            '''
            INSERT INTO receipt(id,RoomNo,ConnectTime,DisconnectTime,RowCount,money,PowerConsumption)
            values(%s,%s,%s,%s,%s,%s,%s)
            '''
            , params=[self.id, self.RoomNo, self.connect_time, self.disconnect_time, self.row_cnt] + list(self.total))
        if self.verbose: print('return from receipt')


if __name__ == '__main__':
    # r = receipt(str(3))
    # r.getReceipt()
    # r.read_receipt('1202006021545')
    r = Receipt(str(1))
    r.getReceipt()
