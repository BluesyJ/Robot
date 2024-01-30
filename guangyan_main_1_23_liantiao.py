
import threading
import yaml
import pickle
from guanyan_classroom_control.ask_chat_with_GPT import *
from guanyan_classroom_control.normal_chat_with_GPT_liantiao import *
from guanyan_classroom_control.ask_chat_with_GPT import *
from new_knowledge.lib_tcp import *
from new_knowledge.tcp_mult import *


with open(r'C:\\Users\Administrator\Desktop\\机器人框架v2\\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config_guanyan5 = yaml.safe_load(config_file)
car15_host = config_guanyan5['car_knowledge']['car15_host']
computer_host = config_guanyan5['car_knowledge']['computer_host']
locations = config_guanyan5['car_knowledge']['locations'] #   待修改
print(locations)
# 设置服务端地址和端口

voice_tcp_car15 = TCP(8889) # 给小车开的端口为8889
ord_tcp_send = TCP(8890)  

car15_flag = 0
get_queue_flag = 0
desired_name = 0
student_question = ""
client_socket = None
# 监听别的信号的线程
shared_queue = queue.Queue()
server = TCPServer(shared_queue) # 改成产线的ip和端口号
server_thread = threading.Thread(target=server.start)
server_thread.start()

#
def listen_ord_tcp(shared_queue):
    global car15_flag, desired_name, student_question, get_queue_flag, client_socket
    while True:
        if get_queue_flag == 0:
            if not shared_queue.empty(): # 清队列有bug
                client_socket, data = shared_queue.get()
                ord_data = data
                print(ord_data)
                desired_name = ord_data["id"] # 去哪个编号的产线设备，id号要等于位置号
                print(desired_name)
                student_question = ord_data["question"] # 产线设备提出的问题
                print(student_question)
                car15_flag = 1
                get_queue_flag = 1

# 判断指令并发送
def car15_control():
    global car15_flag, ord_tcp_send, voice_tcp_car15, desired_name, student_question, get_queue_flag, client_socket
    while True:
        user_reply, _ = voice_tcp_car15.wait_for_1s()
        if user_reply is not None:
            normal_chat_with_GPT(text_input=user_reply, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car15, host=car15_host) # host 为小车ip
        if car15_flag == 0:
            continue
        elif car15_flag == 1:
            car15_flag = 0
            desired_location = next(item["location"] for item in locations if item["name"] == desired_name)
            ord_tcp_send.send_str(car15_host,desired_location)
            ord_tcp_send.wait()
            ask_chat_with_GPT(text_input=student_question, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car15, host=car15_host)
            # time.sleep(5)
            get_queue_flag = 0
            client_socket.send('ok'.encode())
            desired_location = next(item["location"] for item in locations if item["name"] == 0)
            ord_tcp_send.send_str(car15_host, desired_location)
            ord_tcp_send.wait()

# # 判断指令并发送
# def car1_control():
#     global car1_flag, car2_flag, ord_tcp_send, voice_tcp_car1, desired_name, student_question, get_queue_flag, client_socket
#     while True:
#         user_reply, _ = voice_tcp_car1.wait_for_1s()
#         if user_reply is not None:
#             normal_chat_with_GPT(text_input=user_reply, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car1, host=car2_host)
#         if car2_flag == 0:
#             continue
#         elif car2_flag == 1:
#             car2_flag = 0
#             desired_location = next(item["location"] for item in locations if item["name"] == desired_name)
#             ord_tcp_send.send_str(car2_host, desired_location)
#             ord_tcp_send.wait()
#             ask_chat_with_GPT(text_input=student_question, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car1, host=car2_host)
#             # time.sleep(5)
#             get_queue_flag = 0
#             client_socket.send('ok'.encode())


if __name__ == "__main__":

    t1 = threading.Thread(target=car15_control)
    t1.start()
    t2 = threading.Thread(target=listen_ord_tcp,args=(shared_queue, ))
    t2.start()


