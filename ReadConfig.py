import configparser


class Config:
    @staticmethod
    def getDatebase():
        cf = configparser.ConfigParser()
        cf.read("systemconfig.ini", encoding="utf-8")
        database = cf.items("DATABASE")
        database = dict(database)
        return database

    @staticmethod
    def getDispatch():
        cf = configparser.ConfigParser()
        cf.read("systemconfig.ini", encoding="utf-8")
        dispatch = cf.items("DISPATCH")
        dispatch = dict(dispatch)
        return dispatch

    @staticmethod
    def getTempcontrol():
        cf = configparser.ConfigParser()
        cf.read("systemconfig.ini", encoding="utf-8")
        tempcontrol = cf.items("TEMPCONTROL")
        tempcontrol = dict(tempcontrol)
        return tempcontrol

    @staticmethod
    def getBegintemp():
        cf = configparser.ConfigParser()
        cf.read("systemconfig.ini", encoding="utf-8")
        beginTemp = cf.items("BEGINTEMP")
        beginTemp = dict(beginTemp)
        return beginTemp

    @staticmethod
    def getTest():
        cf = configparser.ConfigParser()
        cf.read("systemconfig.ini", encoding="utf-8")
        test = cf.items("TEST")
        test = dict(test)
        return test

if __name__ == '__main__':
    print(Config.getDatebase())
