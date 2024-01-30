import pickle
import queue
import socket
import threading
import time

class TCPServer:
    def __init__(self, shared_queue, host='192.168.1.100', port=8890):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (host, port)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)
        self.shared_queue = shared_queue

    def handle_client(self, client_socket, client_address):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            # 将接收到的数据放入队列
            self.shared_queue.put((client_socket, data))


    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

def process_shared_data(shared_queue):
    while True:
        client_address, data = shared_queue.get()
        data = pickle.loads(data)
        print(f"处理来自 {client_address[0]}:{client_address[1]} 的数据：{data}")
        time.sleep(10)
        print("计时结束")


if __name__ == "__main__":
    shared_queue = queue.Queue()
    server = TCPServer(shared_queue)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    data_processor_thread = threading.Thread(target=process_shared_data, args=(shared_queue,))
    data_processor_thread.start()
