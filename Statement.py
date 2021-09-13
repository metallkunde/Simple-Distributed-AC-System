from Mapper import Mapper
from calendar import monthrange
import datetime


class Statement:  # 报表类
    """
    日报表，要求在一个日报表中能展示所有房间使用空调的次数（一次开关）、最常用目标温度（该房间使用时间最长的目标温度）、
    最常用风速（时间最长的风速）、达到目标温度次数、被调度次数、详单记录数、总费用。
    """

    def __init__(self, start_date):
        self.start_date = start_date
        self.end_date = start_date
        self.detail = []
        self.total = ''
        self.list_row_cnt = 0
        self.room_num = 10
        self.verbose = False

    def getTimeRange(self):
        """
        TimeRange
        """
        pass

    def getDetail(self):
        """
        获取detail
        """
        self.getTimeRange()
        self.start_detail()
        if self.verbose:
            print("时间范围", self.start_date, self.end_date)
        self.fill_detail()
        if self.verbose:
            print(self.detail)
            print(self.list_row_cnt)

    def start_detail(self):
        """
        初始化detail
        """
        self.list_row_cnt = self.room_num  # 房间数量
        self.detail = [[i, 0, 0, 0, 0, 0, 0, 0] for i in range(1, self.list_row_cnt + 1)]

    def fill_detail(self):
        """
        将信息填充到detail中
        """
        mapper = Mapper()
        self.sleeping_to_detail(mapper)
        self.close_to_detail(mapper)
        self.speed_to_detail(mapper)
        self.tempeture_to_detail(mapper)
        self.control_to_detail(mapper)
        self.money_to_detail(mapper)
        self.receipt_to_detail(mapper)

    def receipt_to_detail(self, mapper):
        """

        :param mapper:
        """
        receipt_row_count, receipt = self.get_receipt_and_num(mapper)
        for i in range(receipt_row_count):
            self.detail[receipt[i][0] - 1][6] = receipt[i][1]
        if self.verbose:
            print("7")

    def money_to_detail(self, mapper):
        """

        :param mapper:
        """
        money_row_count, money = self.get_money_sum(mapper)
        for i in range(money_row_count):
            self.detail[money[i][0] - 1][7] = money[i][1]
        if self.verbose:
            print("6")

    def control_to_detail(self, mapper):
        """

        :param mapper:
        """
        DispatchCNT_row_cnt, DispatchCNT = self.get_control_num(mapper)
        for i in range(DispatchCNT_row_cnt):
            self.detail[DispatchCNT[i][0] - 1][5] = DispatchCNT[i][1]
        if self.verbose:
            print("5")

    def tempeture_to_detail(self, mapper):
        """

        :param mapper:
        """
        common_temp_row_count, common_temp = self.get_tempeture_room(mapper)
        for i in range(common_temp_row_count):
            self.detail[common_temp[i][0] - 1][2] = common_temp[i][1]
        if self.verbose:
            print("4")

    def speed_to_detail(self, mapper):
        """

        :param mapper:
        """
        common_wind_speed_row_count, common_wind_speed = self.get_windspeed_room(mapper)
        for i in range(common_wind_speed_row_count):
            self.detail[common_wind_speed[i][0] - 1][3] = common_wind_speed[i][1]
        if self.verbose:
            print("3")

    def close_to_detail(self, mapper):
        """

        :param mapper:
        """
        usageCNT_row_cnt, usageCNT = self.get_close_room(mapper)
        for i in range(usageCNT_row_cnt):
            self.detail[usageCNT[i][0] - 1][1] = usageCNT[i][1]
        if self.verbose:
            print("2")

    def sleeping_to_detail(self, mapper):
        """

        :param mapper:
        """
        achieve_row_cnt, achieve = self.get_sleeping_room(mapper)
        for i in range(achieve_row_cnt):
            self.detail[achieve[i][0] - 1][4] = achieve[i][1]

    def get_receipt_and_num(self, mapper):
        """
        详单记录数、
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT RoomNo,sum(RowCount)
            from receipt 
            where disconnectTime>%s and disconnectTime<=%s
            GROUP BY RoomNo
            '''
            , params=[self.start_date, self.end_date])

    def get_money_sum(self, mapper):
        """
        总费用。sum（money）
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT RoomNo,sum(money)
            from log 
            where msgTime>%s and msgTime<=%s
            GROUP BY RoomNo;
            '''
            , params=[self.start_date, self.end_date])

    def get_control_num(self, mapper):
        """
        被调度次数
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT roomNo,count(*) as CNT
            from WindControl
            where msgTime>%s and msgTime<=%s and WindSpeed>0
            GROUP BY RoomNo
            '''
            , params=[self.start_date, self.end_date])

    def get_tempeture_room(self, mapper):
        """
        最常用目标温度（该房间使用时间最长的目标温度）
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT RoomNo,TargetTemp,max(CNT)
                from (
                    SELECT RoomNo,TargetTemp,COUNT(*) AS CNT
                    from log 
                    where msgTime>%s and msgTime<=%s 
                    GROUP BY RoomNo,TargetTemp
                    ORDER BY RoomNo,CNT DESC
                ) as a
                GROUP BY RoomNo,TargetTemp
            '''
            , params=[self.start_date, self.end_date])

    def get_windspeed_room(self, mapper):
        """
        获得房间号与风速
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT RoomNo,WindSpeed,max(CNT)
            from (
                SELECT RoomNo,WindSpeed,COUNT(*) AS CNT
                from log 
                where msgTime>%s and msgTime<=%s
                GROUP BY RoomNo,WindSpeed
                ORDER BY RoomNo,CNT DESC
                ) as a
            GROUP BY RoomNo,WindSpeed
            '''
            , params=[self.start_date, self.end_date])

    def get_close_room(self, mapper):
        """
        获得状态为close的room与其数量
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT roomNo,count(*) as CNT
            from control
            where msgTime>%s and msgTime<=%s and state='close'
            GROUP BY RoomNo
            '''
            , params=[self.start_date, self.end_date])

    def get_sleeping_room(self, mapper):
        """
        获得状态为sleeping的room与其数量
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT roomNo,count(*)
            from log 
            where msgTime>%s and msgTime<=%s 
            and state='sleeping' 
            GROUP BY RoomNo
            '''
            , params=[self.start_date, self.end_date])

    def getTotal(self):
        """
        合计金额和耗电量 可以被继承
        """
        # 连接对象
        self.total = Mapper().select_one(
            '''
            select sum(money),sum(PowerConsumption) from log
             where msgTime>%s and msgTime<=%s
            '''
            , params=[self.start_date, self.end_date])


class DailyStatement(Statement):
    def getTimeRange(self):
        """
        处理时间格式
        """
        self.end_date = self.start_date + ' 23:59:59'
        # if (self.verbose): print("时间范围", self.start_date, self.end_date)

    def get_detail_group_by_RoomNo(self):
        """
        按房间号获取detail
        """
        self.getTimeRange()
        self.start_detail()
        if self.verbose:
            print("时间范围", self.start_date, self.end_date)
        self.fill_detail()
        if self.verbose:
            print(self.detail)
            print(self.list_row_cnt)

    def get_windspeed_room(self, mapper):
        """
        获得房间号与风速
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT RoomNo,WindSpeed,max(CNT)
            from (
                SELECT RoomNo,WindSpeed,COUNT(*) AS CNT
                from log 
                where msgTime>%s and msgTime<=%s
                GROUP BY RoomNo,WindSpeed
                ORDER BY RoomNo,CNT DESC
                ) as a
            GROUP BY RoomNo,WindSpeed
            '''
            , params=[self.start_date, self.end_date])

    def get_tempeture_room(self, mapper):
        """
        最常用目标温度（该房间使用时间最长的目标温度）
        :param mapper:
        :return:
        """
        return mapper.select_all(
            '''
            SELECT RoomNo,TargetTemp,max(CNT)
                from (
                    SELECT RoomNo,TargetTemp,COUNT(*) AS CNT
                    from log 
                    where msgTime>%s and msgTime<=%s 
                    GROUP BY RoomNo,TargetTemp
                    ORDER BY RoomNo,CNT DESC
                ) as a
                GROUP BY RoomNo,TargetTemp
            '''
            , params=[self.start_date, self.end_date])


class WeeklyStatment(Statement):
    def getTimeRange(self):
        """
        time
        """
        self.year = 2021
        self.week = int(self.start_date)  # 此处startdate是星期数
        td = datetime.timedelta(weeks=self.week)
        d2 = datetime.datetime(year=2020, month=12, day=28) + td
        self.start_date = str(datetime.datetime(d2.year, d2.month, d2.day))
        d3 = d2 + datetime.timedelta(days=7)
        self.end_date = str(datetime.datetime(d3.year, d3.month, d3.day))


class MonthlyStatement(Statement):  # 时间的格式可能需要处理一下???
    def getTimeRange(self):
        self.month = int(self.start_date)  # 处理字符串
        self.year = 2021
        self.end_date = '2021-' + str(int(self.start_date) + 1) + '-01 00:00:00'
        self.start_date = '2021-' + self.start_date + '-01 00:00:00'

    def get_detail_group_by_day(self):
        """
        获取detail
        """
        self.getTimeRange()
        self.start_detail()
        if self.verbose:
            print("try MonthlyStatement")
        self.fill_detail()
        if self.verbose:
            print(self.detail)
            print(self.list_row_cnt)

    def start_detail(self):
        """
        初始化detail
        """
        self.list_row_cnt = self.room_num  # 房间数量
        self.detail = [[i, 0, 0, 0, 0, 0, 0, 0] for i in range(1, monthrange(self.year, self.month)[1] + 1)]

    # def get_receipt_and_num(self, mapper):
    #     """
    #     详单记录数、
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(disconnectTime),sum(RowCount)
    #         from receipt
    #         where disconnectTime>=%s and disconnectTime<=%s
    #         GROUP BY disconnectTime
    #         ORDER BY day(disconnectTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_money_sum(self, mapper):
    #     """
    #     总费用。sum（money）
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(msgTime),sum(money),sum(PowerConsumption)
    #         from log
    #         where msgTime>%s and msgTime<=%s
    #         GROUP BY msgTime
    #         ORDER BY day(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_control_num(self, mapper):
    #     """
    #     被调度次数
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(msgTime),count(*) as CNT
    #         from WindControl
    #         where msgTime>%s and msgTime<=%s and WindSpeed>0 and flag=1
    #         GROUP BY msgTime
    #         ORDER BY day(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_tempeture_room(self, mapper):
    #     """
    #     最常用目标温度（该房间使用时间最长的目标温度）
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(msgTime),TargetTemp,max(CNT)
    #             from (
    #                 SELECT msgTime,TargetTemp,COUNT(*) AS CNT
    #                 from log
    #                 where msgTime>%s and msgTime<=%s
    #                 GROUP BY msgTime,TargetTemp
    #                 ORDER BY day(msgTime),CNT DESC
    #             ) as a
    #         GROUP BY msgTime,TargetTemp
    #         ORDER BY day(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_windspeed_room(self, mapper):
    #     """
    #     获得房间号与风速
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(msgTime),WindSpeed,max(CNT)
    #         from (
    #             SELECT msgTime,WindSpeed,COUNT(*) AS CNT
    #             from log
    #             where msgTime>%s and msgTime<=%s
    #             GROUP BY msgTime,WindSpeed
    #             ORDER BY day(msgTime),CNT DESC
    #             ) as a
    #         GROUP BY msgTime,WindSpeed
    #         ORDER BY day(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_close_room(self, mapper):
    #     """
    #     获得状态为close的room与其数量
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(msgTime),count(*) as CNT
    #         from control
    #         where msgTime>%s and msgTime<=%s and state='close'
    #         GROUP BY msgTime
    #         ORDER BY day(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_sleeping_room(self, mapper):
    #     """
    #     获得状态为sleeping的room与其数量
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT day(msgTime),count(*)
    #         from log
    #         where msgTime>%s and msgTime<=%s
    #         and state='sleeping'
    #         GROUP BY msgTime
    #         ORDER BY day(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])


class AnnualStatement(Statement):
    def getTimeRange(self):
        # 处理字符串
        self.year = self.start_date
        self.end_date = str(int(self.start_date) + 1) + '-01-01 00:00:00'
        self.start_date = self.start_date + '-01-01 00:00:00'

    def get_detail_group_by_month(self):
        """
        获取detail
        """
        self.getTimeRange()
        self.start_detail()
        if self.verbose:
            print("try AnnualStatement")
        self.fill_detail()
        if self.verbose:
            print(self.detail)
            print(self.list_row_cnt)

    def start_detail(self):
        """
        初始化detail
        """
        self.list_row_cnt = self.room_num  # 房间数量
        self.detail = [[i, 0, 0, 0, 0, 0, 0, 0] for i in range(1, 13)]

    # def get_receipt_and_num(self, mapper):
    #     """
    #     详单记录数、
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(disconnectTime),sum(RowCount)
    #         from receipt
    #         where disconnectTime>=%s and disconnectTime<=%s
    #         GROUP BY disconnectTime
    #         ORDER BY month(disconnectTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_money_sum(self, mapper):
    #     """
    #     总费用。sum（money）
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(msgTime),sum(money),sum(PowerConsumption)
    #         from log
    #         where msgTime>=%s and msgTime<=%s
    #         GROUP BY msgTime
    #         ORDER BY month(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_control_num(self, mapper):
    #     """
    #     被调度次数
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(msgTime),count(*) as CNT
    #         from WindControl
    #         where msgTime>=%s and msgTime<=%s and WindSpeed>0 and flag=1
    #         GROUP BY msgTime
    #         ORDER BY month(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_tempeture_room(self, mapper):
    #     """
    #     最常用目标温度（该房间使用时间最长的目标温度）
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(msgTime),TargetTemp,max(CNT)
    #             from (
    #                 SELECT msgTime,TargetTemp,COUNT(*) AS CNT
    #                 from log
    #                 where msgTime>=%s and msgTime<=%s
    #                 GROUP BY msgTime,TargetTemp
    #                 ORDER BY month(msgTime),CNT DESC
    #             ) as a
    #         GROUP BY msgTime,TargetTemp
    #         ORDER BY month(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_windspeed_room(self, mapper):
    #     """
    #     获得房间号与风速
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(msgTime),WindSpeed,max(CNT)
    #         from (
    #             SELECT msgTime,WindSpeed,COUNT(*) AS CNT
    #             from log
    #             where msgTime>=%s and msgTime<=%s
    #             GROUP BY msgTime,WindSpeed
    #             ORDER BY month(msgTime),CNT DESC
    #             ) as a
    #         GROUP BY msgTime,WindSpeed
    #         ORDER BY month(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_close_room(self, mapper):
    #     """
    #     获得状态为close的room与其数量
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(msgTime),count(*) as CNT
    #         from control
    #         where msgTime>=%s and msgTime<=%s and state='close'
    #         GROUP BY msgTime
    #         ORDER BY month(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])
    #
    # def get_sleeping_room(self, mapper):
    #     """
    #     获得状态为sleeping的room与其数量
    #     :param mapper:
    #     :return:
    #     """
    #     return mapper.select_all(
    #         '''
    #         SELECT month(msgTime),count(*)
    #         from log
    #         where msgTime>=%s and msgTime<=%s
    #         and state='sleeping'
    #         GROUP BY msgTime
    #         ORDER BY month(msgTime)
    #         '''
    #         , params=[self.start_date, self.end_date])