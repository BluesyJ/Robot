from car_voice.audionew import *
from car_voice.baidu_voice2text2words import *
from new_knowledge.lib_tcp import *
from new_knowledge.charge_instruction import *
import threading
from threading import Lock,Thread
import time,os
from new_knowledge.lib_tcp import *
from GPT_API.chat_with_gpt import *
import yaml

with open(r'D:\UserFiles\文件\研究生\工作项目\机器人框架v2\config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)
arm_host = config['car_knowledge']['arm_host']
car_host = config['car_knowledge']['car_host']
computer_host = config['car_knowledge']['computer_host']
# 设置服务端地址和端口
run_flag = 0
listen_voice_flag = "car"
input_text = ''
input_robot = ''
ord_tcp = TCP(8888)
voice_tcp = TCP(8889)

# 泡茶程序
def paocha(tcp):
    list = [{'指令': '移动', '目的地': '厨房', '目的地坐标': "{'x': -1.356573771429246, 'y': 4.999944688176971, 'yaw': 0.7946730148562868, 'z': 0.0}"},
            {'指令': '机械臂操作', '动作流程': "['reach', 'chabao', 'catch', 'put', 'cup', 'release']"},
            {'指令': '机械臂操作', '动作流程': "['reach', 'cup', 'catch']"},
            {'指令': '机械臂操作', '动作流程': "['put', 'water']"},
            {'指令': '机械臂操作', '动作流程': "['put', 'tuopan', 'release']"},
            {'指令': '移动', '目的地': '卧室里', '目的地坐标': "{'x': -1.170713179748654, 'y': 0.04374214671541992, 'yaw': -2.255652161020206, 'z': 0.0}"}]
    for i in list:
        print(i)
        if i["指令"] == "机械臂操作":
            tcp.send_str(arm_host, i["动作流程"])
        elif i["指令"] == "移动":
            tcp.send_str(car_host, i["目的地坐标"])
        tcp.wait()
        time.sleep(1)

# 监听别的信号的线程
def listen_tcp():
    global run_flag, input_text, input_robot, voice_tcp, listen_voice_flag
    while True:
        if listen_voice_flag == "car":
            listen_voice_flag = "None"
            input_text, input_ip = voice_tcp.wait()
            run_flag = 1
            if input_ip == '192.168.3.36':
                input_robot = 'arm'
            elif input_ip == '192.168.3.50':
                input_robot = 'car'

# 判断指令并发送
def send_order():
    global arm_host, car_host, computer_host, run_flag, input_text, listen_voice_flag, ord_tcp
    while True:
        if run_flag == 1:
            run_flag = 0
            list4 = []
            try:
                list3 = []
                try:
                    list1 = get_ord_list(input_text)
                    for i in list1:
                        print(i)
                    list2 = charge_ord(list1)
                    for i in list2:
                        print(i)
                    list3 = handle_list(list2)
                except:
                    print("指令解析失败")
                for i in list3:
                    list4.append(i)
                    print(i)
                    if i["指令"] == "机械臂操作":
                        ord_tcp.send_str(arm_host, i["动作流程"])
                        ord_tcp.wait()
                        time.sleep(1)
                    elif i["指令"] == "移动":
                        ord_tcp.send_str(car_host, i["目的地坐标"])
                        ord_tcp.wait()
                        time.sleep(1)
                    elif i["指令"] == "找人":
                        print("{'目标': '" + str(i["目标"]) + "'}")
                        ord_tcp.send_str(car_host, "{'目标': '" + str(i["目标"]) + "'}")
                        ord_tcp.wait()
                    elif i["指令"] == "泡茶":
                        paocha(ord_tcp)
            except:
                print('无法发送')
            if list4.__len__() != 0:
                listen_voice_flag = "car"
            elif list4.__len__() == 0:
                print("没识别出什么指令,开始问gpt")
                list3 = ask_for_GPT(input_text, ord_tcp, voice_tcp, car_host)
                for i in list3:
                    print(i)
                    if i["指令"] == "机械臂操作":
                        ord_tcp.send_str(arm_host, i["动作流程"])
                        ord_tcp.wait()
                        time.sleep(1)
                    elif i["指令"] == "移动":
                        ord_tcp.send_str(car_host, i["目的地坐标"])
                        ord_tcp.wait()
                        time.sleep(1)
                    elif i["指令"] == "找人":
                        print("{'目标': '" + str(i["目标"]) + "'}")
                        ord_tcp.send_str(car_host, "{'目标': '" + str(i["目标"]) + "'}")
                        ord_tcp.wait()
                listen_voice_flag = "car"


t1 = threading.Thread(target=send_order)
t1.start()
t3 = threading.Thread(target=listen_tcp)
t3.start()

























