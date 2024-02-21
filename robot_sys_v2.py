import threading
import yaml
import pickle
from guanyan_classroom_control.ask_chat_with_GPT import *
from guanyan_classroom_control.ask_chat_with_GPT import *
from new_knowledge.lib_tcp import *
from new_knowledge.tcp_mult import *
from robot_gpt_v3 import *


with open(r'C:\\Users\Administrator\Desktop\\机器人框架v2\\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config_guanyan5 = yaml.safe_load(config_file)
car15_host = config_guanyan5['car_knowledge']['car15_host']
computer_host = config_guanyan5['car_knowledge']['computer_host']
locations = config_guanyan5['car_knowledge']['locations'] #   待修改
print(locations)



# 消息队列相关初始化

mq_car15_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "car15_to_sys")
mq_car16_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "car16_to_sys")
mq_gpt_to_car_move = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car_move")
mq_gpt_to_car_read = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car_read")

car15_flag = 0
get_queue_flag = 0
desired_name = 0
student_question = ""
client_socket = None
# 监听别的信号的线程
# shared_queue = queue.Queue()
# server = TCPServer(shared_queue) # 改成产线的ip和端口号 , 后面要改成产线格式的消息队列
# server_thread = threading.Thread(target=server.start)
# server_thread.start()

#
def listen_ord_tcp(shared_queue): #待修改
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
    mq_car15_to_sys.connect()
    while True:
        method_frame, header_frame, body = mq_car15_to_sys.channel.basic_get(queue=mq_car15_to_sys.queue, auto_ack=True)
        print("等待接收")
        if method_frame:
            user_input = body.decode('utf-8')
            normal_chat_with_GPT(text_input=user_input) # host 为小车ip
        time.sleep(1)
        # if car15_flag == 0:
        #     continue
        # elif car15_flag == 1:
        #     car15_flag = 0
        #     desired_location = next(item["location"] for item in locations if item["name"] == desired_name)
        #     ord_tcp_send.send_str(car15_host,desired_location)
        #     ord_tcp_send.wait()
        #     ask_chat_with_GPT(text_input=student_question, ord_tcp=ord_tcp_send, voice_tcp=voice_tcp_car15, host=car15_host)
        #     # time.sleep(5)
        #     get_queue_flag = 0
        #     client_socket.send('ok'.encode())
        #     desired_location = next(item["location"] for item in locations if item["name"] == 0)
        #     ord_tcp_send.send_str(car15_host, desired_location)
        #     ord_tcp_send.wait()


if __name__ == "__main__":

    t1 = threading.Thread(target=car15_control)
    t1.start()
    # t2 = threading.Thread(target=listen_ord_tcp,args=(shared_queue, ))
    # t2.start()


