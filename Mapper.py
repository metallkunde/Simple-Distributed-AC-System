import pymysql
import ReadConfig


class Mapper():  # 封装一下数据库操作
    def __init__(self):
        config = ReadConfig.Config.getDatebase()
        self.host, self.database, self.user, self.password, self.port, self.charset = config['host'], config[
            'database'], config['user'], config['passwd'], int(config['port']), config['charset']

    # 连接数据库
    def connect(self):
        self.conn = pymysql.connect(host=self.host, database=self.database, user=self.user, password=self.password,
                                    port=self.port, charset=self.charset)
        self.cursor = self.conn.cursor()

    # 关闭
    def close(self):
        self.cursor.close()
        self.conn.close()

    # 查询一条数据模板
    def select_one(self, sql, params=[]):
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()  # 查询一条数据
            self.close()
        except Exception as ex:
            print(ex)
            pass
        return result

    # 查询所有数据模板
    def select_all(self, sql, params=None):
        result = ()
        try:
            self.connect()
            row_count = self.cursor.execute(sql, params)
            result = self.cursor.fetchall()  # 查询所有数据
            self.close()
        except Exception as ex:
            print(ex)
            pass
        return row_count, result

    # 增删改代码的封装
    def __edit(self, sql, params):
        count = 0
        try:
            # self.connect()
            count = self.cursor.execute(sql, params)
            self.conn.commit()
            # self.close()
        except Exception as ex:
            print(ex)
            pass
        return count

    # 增
    def insert(self, sql, params=[]):
        return self.__edit(sql, params)

    # 改
    def update(self, sql, params=[]):
        return self.__edit(sql, params)

    # 删
    def delete(self, sql, params=[]):
        return self.__edit(sql, params)
