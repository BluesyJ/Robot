import os
import cv2
import socket
import os
import sys
import struct

server_host = "192.168.88.183"
server_port = 8888

def sock_client_image(img_path):
    global server_host, server_port
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_host, server_port))  # 服务器和客户端在不同的系统或不同的主机下时使用的ip和端口，首先要查看服务器所在的系统网卡的ip
            # s.connect(('127.0.0.1', 8001))  #服务器和客户端都在一个系统下时使用的ip和端口
        except socket.error as msg:
            print(msg)
            print(sys.exit(1))

        fhead = struct.pack(b'128sq', bytes(os.path.basename(img_path), encoding='utf-8'),
                            os.stat(img_path).st_size)  # 将xxx.jpg以128sq的格式打包
        s.send(fhead)

        fp = open(img_path, 'rb')  # 打开要传输的图片
        while True:
            data = fp.read(1024)  # 读入图片数据
            if not data:
                print('{0} send over...'.format(img_path))
                break
            s.send(data)  # 以二进制格式发送图片数据
        s.close()
        break

if __name__ == "__main__":
    sock_client_image("1.jpg")