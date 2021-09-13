import StopThreading
import socket
import threading


class UdpClient():
    def __init__(self, signals):
        super(UdpClient, self).__init__()
        self.udp_socket = None  # socket
        self.address = None  # tuple类型 (str(ip), int(port))
        self.listen_thread = None  # 监听服务器线程
        # 信号槽机制：设置一个信号，用于触发接收区写入动作
        self.signal_write = signals

    # 用于创建一个线程持续监听UDP通信
    def udp_client_listen_concurrency(self):
        while True:
            try:
                recv_msg, recv_addr = self.udp_socket.recvfrom(1024)
                msg = recv_msg.decode('utf-8')
                # msg = '来自IP:{}端口:{}:\n{}\n'.format(recv_addr[0], recv_addr[1], msg)
                self.signal_write.emit(msg)
            except:
                msg = '服务端连接关闭'
                self.signal_write.emit(msg)

    # 连接服务端：向服务端发送* hi 收到以# 开头的设置参数连接成功
    def udp_client_start(self, ip, port, roomID):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 尝试连接服务端
            self.address = (str(ip), int(port))
            self.udp_send('* hi ' + str(roomID))
            self.udp_socket.settimeout(1)
            # 如果1s内收到回复
            recv_msg, recv_addr = self.udp_socket.recvfrom(1024)
            recv_msg = recv_msg.decode('utf-8')
            self.udp_socket.settimeout(None)
            # 回复为正确内容，开启监听线程
            if recv_msg[0] == "#":
                self.signal_write.emit(recv_msg)
                self.client_th = threading.Thread(target=self.udp_client_listen_concurrency)
                self.client_th.start()
                return 1

        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            self.signal_write.emit(msg)
            self.udp_socket.close()
            return 0

    # 向服务端发送信息
    def udp_send(self, textEdit):
        try:
            send_msg = textEdit.encode('utf-8')
            self.udp_socket.sendto(send_msg, self.address)
            msg = '消息已发送\n'
            self.signal_write.emit(msg)

        except Exception as ret:
            msg = '发送失败\n'
            self.signal_write.emit(msg)

    # 关闭客户端连接：1、关闭socket 2、关闭监听线程
    def udp_client_close(self):
        # 关闭网络连接
        try:
            self.udp_socket.close()
            StopThreading.stop_thread(self.client_th)
            msg = '已断开网络\n'
            self.signal_write.emit(msg)
        except Exception as ret:
            pass
        else:
            pass
