from Receipt import Receipt


def float_to_round(x, n):
    """
    如果输入的x是浮点数返回保留n位的浮点数
    :param x: 输入的数字
    :param n: 保留几位小数
    :return: 返回保留后的结果
    """
    if isinstance(x, float):
        r = round(x, n)
    else:
        r = x
    return r

def t_day(datetime):
    """

    :param datetime: 时间
    :return: 查询的日报表时间的字符串
    """
    return datetime.date().toString("yyyy-MM-dd")

def t_month(datetime):
    """

    :param datetime: 时间
    :return: 按月查询的日报表时间的字符串
    """
    return datetime.date().toString("MM")

def t_year(datetime):
    """

    :param datetime: 时间
    :return: 按年查询的日报表时间的字符串
    """
    return datetime.date().toString("yyyy")


def fee_show_table_on_ui(b, fee):
    """
    展示费用
    :param b:
    :param fee:
    """
    if fee is not None:  # 返回值不为None时
        b.setText(str(round(fee, 2)))  # 金额保留两位小数
    else:
        b.setText("暂无数据")

def get_receipt(room):
    """
    计算账单详单
    :param room: 房间号
    :return:
    """
    r = Receipt(room)
    r.getReceipt()
    return r