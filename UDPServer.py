import StopThreading
import socket
import threading


class UdpServer:
    """
    中央空调的UDP通信
    """

    def __init__(self, signals):
        super(UdpServer, self).__init__()
        self.udp_socket = None  # socket
        self.address = None  # 待发送信息的ip地址
        self.sever_th = None  # 监听线程
        self.connectClient = dict()
        self.signal_write_msg = signals

    def udp_server_listen_start(self, port):
        """
        开启服务端
        :param port:
        :return:
        """
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.udp_socket.bind(('', int(port)))
        except Exception as ret:
            self.signal_write_msg.emit('请检查端口号\n')
            return 0
        else:
            self.sever_th = threading.Thread(target=self.udp_server_listen_concurrency)
            self.sever_th.start()
            self.signal_write_msg.emit('UDP服务端正在监听端口:{}\n'.format(port))
            return 1

    def udp_server_listen_concurrency(self):
        """
        用于创建一个线程持续监听UDP通信
        """
        while True:
            try:
                recv_msg, recv_addr = self.udp_socket.recvfrom(1024)
            except:
                print("远程主机强迫关闭了一个现有的连接")
            else:
                self.signal_write_msg.emit(
                    self.get_signal_write_msg(recv_addr, recv_msg))
                if recv_addr not in self.connectClient.values():
                    self.address = (str(recv_addr[0]), int(recv_addr[1]))

    @staticmethod
    def get_signal_write_msg(recv_addr, recv_msg):
        """
        对端口和信息进行处理返回字符串
        :param recv_addr:
        :param recv_msg:
        :return:
        """
        return 'IP ' + str(recv_addr[0]) + ' PORT ' + str(recv_addr[1]) + ' ' + recv_msg.decode('utf-8')

    def udp_send(self, textedit):
        """
        向self.address发送信息
        :param textedit:
        """
        try:
            self.udp_socket.sendto(textedit.encode('utf-8'), self.address)
            self.signal_write_msg.emit('消息已发送')
        except Exception as ret:
            self.signal_write_msg.emit('发送失败\n')

    def udp_sendall(self, text):
        """
        向连接的所有客户端发送相同信息
        :param text:
        """
        for address in self.connectClient.values():
            self.address = address
            self.udp_send(text)

    def udp_server_close(self):
        """
        关闭客户端连接：
            1、关闭socket
            2、关闭监听线程
        """
        try:
            self.udp_socket.close()
            StopThreading.stop_thread(self.sever_th)
            self.connectClient = {}  # 清空连接名单
            self.signal_write_msg.emit('已断开网络\n')
        except Exception as ret:
            pass
