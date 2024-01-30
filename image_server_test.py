import socket
import os
import sys
import struct

def send_string_to_server(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 连接到服务器
        s.connect((ip, port))
        
        # 发送消息
        s.sendall(message.encode())

        # 可选：接收服务器的响应
        data = s.recv(1024)

    print('Received', repr(data))

# 使用函数发送字符串


def socket_service_image():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.bind(('127.0.0.1', 8001))
        s.bind(('192.168.50.109', 8001))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    print("Wait for Connection.....................")

    while True:
        sock, addr = s.accept()  # addr是一个元组(ip,port)
        deal_image(sock, addr)


def deal_image(sock, addr):
    print("Accept connection from {0}".format(addr))  # 查看发送端的ip和端口

    while True:
        fileinfo_size = struct.calcsize('128sq')
        buf = sock.recv(fileinfo_size)  # 接收图片名
        if buf:
            filename, filesize = struct.unpack('128sq', buf)
            fn = filename.decode().strip('\x00')
            new_filename = os.path.join(r'E:' + fn)  # 在服务器端新建图片名（可以不用新建的，直接用原来的也行，只要客户端和服务器不是同一个系统或接收到的图片和原图片不在一个文件夹下）

            recvd_size = 0
            fp = open(new_filename, 'wb')

            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = sock.recv(1024)
                    recvd_size += len(data)
                else:
                    data = sock.recv(1024)
                    recvd_size = filesize
                fp.write(data)  # 写入图片数据
            fp.close()
        sock.close()
        break
if __name__ == '__main__':
    # send_string_to_server('192.168.50.109', 8888, "{'pitch': 0.0, 'roll': 0.0, 'x': 30.84053731907167, 'y': -8.494407711305142, 'yaw': 0.9118755816478443, 'z': 0.0, 'gpt4':0}")
    socket_service_image()