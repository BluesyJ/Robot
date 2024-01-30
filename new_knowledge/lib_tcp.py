import socket
import pickle
class TCP():
    def __init__(self, port=8888) :
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.host = socket.gethostbyname(socket.gethostname())
        self.host = "192.168.50.32"
        self.port = port  # 监听端口号
        self.server_address = (self.host,self. port)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)
        print(f"服务器正在监听 {self.host}:{self.port}...")

    def send_str(self, host, text):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, self.port)
        # 设置连接超时
        client_socket.settimeout(1.0)
        try:
            client_socket.connect(server_address)
            print("连接成功")
            client_socket.sendall(text.encode())
            print("发送")
        except socket.timeout:
            print("连接超时，超过1秒未能连接到服务器")
        except Exception as e:
            print("连接过程中发生错误:", e)
        finally:
            client_socket.close()
            print("关闭")

    def wait(self):
        # 等待客户端连接请求
        client_socket, client_address = self.server_socket.accept()
        print(f"与客户端 {client_address[0]}:{client_address[1]} 建立连接！")
        # 持续接收指令，直到客户端关闭连接
        data = client_socket.recv(1024)
        command = data.decode()
        print("接收到的指令：", command)
        # 关闭连接
        client_socket.close()
        print(f"与客户端 {client_address[0]}:{client_address[1]} 的连接已关闭！")
        input_ip = f" {client_address[0]}:{client_address[1]} "
        return command, input_ip

    def wait_for_1s(self, timeout=1.0):
        # 临时设置超时时间
        original_timeout = self.server_socket.gettimeout()
        self.server_socket.settimeout(timeout)
        try:
            # 等待客户端连接请求
            client_socket, client_address = self.server_socket.accept()
            print(f"与客户端 {client_address[0]}:{client_address[1]} 建立连接！")
            # 持续接收指令，直到客户端关闭连接
            data = client_socket.recv(1024)
            command = data.decode()
            print("接收到的指令：", command)
            # 关闭连接
            client_socket.close()
            print(f"与客户端 {client_address[0]}:{client_address[1]} 的连接已关闭！")
            input_ip = f" {client_address[0]}:{client_address[1]} "
            return command, input_ip
        except socket.timeout:
            print("等待超时，没有收到数据")
            return None, None
        finally:
            # 恢复原始超时设置
            self.server_socket.settimeout(original_timeout)

    def wait_pickle(self):
        # 等待客户端连接请求
        client_socket, client_address = self.server_socket.accept()
        print(f"与客户端 {client_address[0]}:{client_address[1]} 建立连接！")
        # 持续接收指令，直到客户端关闭连接
        data = client_socket.recv(4096)
        command = pickle.loads(data)
        print("接收到的指令：", command)
        # 关闭连接
        client_socket.close()
        print(f"与客户端 {client_address[0]}:{client_address[1]} 的连接已关闭！")
        input_ip = f" {client_address[0]}:{client_address[1]} "
        return command, input_ip


if __name__=="__main__":
    # 设置服务端地址和端口
    host1 = '192.168.1.109'  # 移动机器人1地址
    host2 = '192.168.1.108'  # 移动机器人2地址
    host3 = '192.168.1.100'  # 移动机器人2地址
    # tcp = TCP(8890)
    # tcp.send_str(host2, "{'x': -3.068164131970748, 'y': 5.236507532827794, 'yaw': 1.695281611984841, 'z': 0.0}")
    # tcp.send_str(host2, "刘秀坤这个小沟八")
    # tcp.send_str(host3, "刘秀坤这个小沟八")
    # a, _ = tcp.wait_for_1s()
    # print("ok")

    # tcp = TCP(8890)
    # ord_data, input_ip = tcp.wait_pickle()
    # print(ord_data)
    # desired_name = ord_data["id"]
    for i in range(4):
        tcp = TCP(8890)
        # tcp.send_str(host3, "刘秀坤这个小沟八")