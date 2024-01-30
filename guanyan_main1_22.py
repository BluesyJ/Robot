import threading
import yaml
import pickle
from guanyan_classroom_control.ask_chat_with_GPT import *
from guanyan_classroom_control.normal_chat_with_GPT import *
from guanyan_classroom_control.ask_chat_with_GPT import *
from new_knowledge.lib_tcp import *
from new_knowledge.tcp_mult import *


with open(r'D:\UserFiles\文件\研究生\工作项目\机器人框架v2\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config_guanyan5 = yaml.safe_load(config_file)
car1_host = config_guanyan5['car_knowledge']['car1_host']
car2_host = config_guanyan5['car_knowledge']['car2_host']
computer_host = config_guanyan5['car_knowledge']['computer_host']
locations = config_guanyan5['car_knowledge']['locations']
# 设置服务端地址和端口
ord_tcp_send = TCP(8888)
voice_tcp_car1 = TCP(8891)
voice_tcp_car2 = TCP(8892)
car1_flag = 0
car2_flag = 0
get_queue_flag = 0
desired_name = 0
student_question = ""
client_socket = None
# 监听别的信号的线程
shared_queue = queue.Queue()
server = TCPServer(shared_queue)
server_thread = threading.Thread(target=server.start)
server_thread.start()

#
def listen_ord_tcp(shared_queue):
    global car1_flag, car2_flag, desired_name, student_question, get_queue_flag, client_socket
    while True:
        if get_queue_flag == 0:
            if not shared_queue.empty():
                client_socket, data = shared_queue.get()
                ord_data = data
                print(ord_data)
                desired_name = ord_data["id"]
                student_question = ord_data["question"]
                car2_flag = 1
                get_queue_flag = 1

# 判断指令并发送
def car2_control():
    global car1_flag, car2_flag, ord_tcp_send, voice_tcp_car2, desired_name, student_question, get_queue_flag, client_socket
    while True:
        user_reply, _ = voice_tcp_car2.wait_for_1s()
        if user_reply is not None:
            normal_chat_with_GPT(text_input=user_reply, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car2, host=car2_host)
        if car2_flag == 0:
            continue
        elif car2_flag == 1:
            car2_flag = 0
            desired_location = next(item["location"] for item in locations if item["name"] == desired_name)
            ord_tcp_send.send_str(car2_host,desired_location)
            ord_tcp_send.wait()
            ask_chat_with_GPT(text_input=student_question, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car2, host=car2_host)
            # time.sleep(5)
            get_queue_flag = 0
            client_socket.send('ok'.encode())





t1 = threading.Thread(target=car2_control)
t1.start()
t2 = threading.Thread(target=listen_ord_tcp,args=(shared_queue, ))
t2.start()

























