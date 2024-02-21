import threading
import yaml
import pickle
from guanyan_classroom_control.ask_chat_with_GPT import *
from guanyan_classroom_control.ask_chat_with_GPT import *
from new_knowledge.lib_tcp import *
from new_knowledge.tcp_mult import *
from robot_gpt_v3 import *
import os  
# 读取本地配置文件
with open(r'C:\\Users\Administrator\Desktop\\机器人框架v2\\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config_guanyan5 = yaml.safe_load(config_file)
car15_host = config_guanyan5['car_knowledge']['car15_host']
computer_host = config_guanyan5['car_knowledge']['computer_host']
locations = config_guanyan5['car_knowledge']['locations'] #   待修改
print(locations)

# 消息队列相关初始化
mq_car15_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "car15_to_sys")
mq_car16_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "car16_to_sys")
mq_find_sys_to_car15 = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "find_sys_to_car15") # 主要涉及三级地点的调度
mq_find_sys_to_car16 = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "find_sys_to_car16") # 主要涉及三级地点的调度
mq_find_car15_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "find_car15_to_sys") # 主要负责到点后的图像保存
mq_find_car16_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "find_car16_to_sys") # 主要负责到点后的图像保存
mq_gpt_to_car15_move = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car15_move")
mq_gpt_to_car16_move = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car16_move")
mq_gpt_to_car15_read = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car15_read")
mq_gpt_to_car16_read = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car16_read")
mq_gpt_to_car15_move.connect()
mq_gpt_to_car16_move.connect()
mq_gpt_to_car15_read.connect()
mq_gpt_to_car16_read.connect()
mq_car15_to_sys.connect()
mq_car16_to_sys.connect()

# 判断指令并发送
def sys_to_car15():
    mq_car15_to_sys.connect()
    while True:
        method_frame, header_frame, body = mq_car15_to_sys.channel.basic_get(queue=mq_car15_to_sys.queue, auto_ack=True)
        print("等待接收")
        if method_frame:
            user_input = body.decode('utf-8')
            gpt_reply_dic = normal_chat_with_GPT(text_input=user_input) # host 为小车ip
            print(gpt_reply_dic)
            if gpt_reply_dic is not None: # 判断是否为噪音
                print("进了1")

                if gpt_reply_dic["行为"] == "移动" or gpt_reply_dic["行为"] == "观察":
                    print("进了")
                    try:
                        os.remove("received_image.jpg")
                    except:
                        print("文件已经清理完毕")
                        
                    if gpt_reply_dic["对象"] != "无": # 刘秀坤程序
                        pass 

                    elif gpt_reply_dic["楼层"] == "15楼":
                        if gpt_reply_dic["二级地点"] != "无":
                            location2 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["二级地点"])
                            mq_gpt_to_car15_move.send_text(location2)
                        elif gpt_reply_dic["一级地点"] != "无":
                            location1 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["一级地点"])
                            mq_gpt_to_car15_move.send_text(location1)
                        else: # 没有目的地，停留在原地
                            pass
                        start_time = time.time()
                        while True:
                            mq_find_sys_to_car15.connect()
                            mq_find_sys_to_car15.send_text('look')
                            print("send to 15")
                            if time.time() - start_time > 2:
                                break  # 超时后退出循环
                            time.sleep(1)
                        while not os.path.isfile("received_image.jpg"):
                            pass
                        print("是读图片的时候了！")
                        base64_image = encode_image("received_image.jpg")
                        gpt_photo_reply = GPT_photo_and_language(base64_image=base64_image, question=gpt_reply_dic["意图"])
                        mq_gpt_to_car15_read.send_text(gpt_photo_reply)
                        
                    elif gpt_reply_dic["楼层"] == "16楼":
                        if gpt_reply_dic["二级地点"] != "无":
                            location2 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["二级地点"])
                            mq_gpt_to_car16_move.send_text(location2)
                        elif gpt_reply_dic["一级地点"] != "无":
                            location1 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["一级地点"])
                            mq_gpt_to_car16_move.send_text(location1)
                        start_time = time.time()
                        while True:
                            mq_find_sys_to_car16.connect()
                            mq_find_sys_to_car16.send_text('look')
                            print("send to 16")
                            if time.time() - start_time > 2:
                                break  # 超时后退出循环
                            time.sleep(1)
                        while not os.path.isfile("received_image.jpg"):
                            pass
                        print("是读图片的时候了！")
                        base64_image = encode_image("received_image.jpg")
                        gpt_photo_reply = GPT_photo_and_language(base64_image=base64_image, question=gpt_reply_dic["意图"])
                        mq_gpt_to_car15_read.send_text(gpt_photo_reply)
                else: # 行为为无法完成时，即去一些不存在的点位
                    print("行为无法完成")
                        
        time.sleep(1)

def sys_to_car16(): # 待修改
    mq_car16_to_sys.connect()
    while True:
        method_frame, header_frame, body = mq_car16_to_sys.channel.basic_get(queue=mq_car16_to_sys.queue, auto_ack=True)
        print("等待接收")
        if method_frame:
            user_input = body.decode('utf-8')
            gpt_reply_dic = normal_chat_with_GPT(text_input=user_input) # host 为小车ip
            print(gpt_reply_dic)
            if gpt_reply_dic is not None: # 判断是否为噪音
                print("进了1")
                if gpt_reply_dic["行为"] == "移动" or gpt_reply_dic["行为"] == "观察":
                    print("进了")
                    try:
                        os.remove("received_image.jpg")
                    except:
                        print("文件已经清理完毕")
                    if gpt_reply_dic["对象"] != "无": # 刘秀坤程序
                        pass 
                    elif gpt_reply_dic["楼层"] == "15楼":
                        if gpt_reply_dic["二级地点"] != "无":
                            location2 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["二级地点"])
                            mq_gpt_to_car15_move.send_text(location2)
                        elif gpt_reply_dic["一级地点"] != "无":
                            location1 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["一级地点"])
                            mq_gpt_to_car15_move.send_text(location1)
                        else: # 没有目的地，停留在原地
                            pass
                        start_time = time.time()
                        while True:
                            mq_find_sys_to_car15.connect()
                            mq_find_sys_to_car15.send_text('look')
                            print("send to 15")
                            if time.time() - start_time > 2:
                                break  # 超时后退出循环
                            time.sleep(1)
                        while not os.path.isfile("received_image.jpg"):
                            pass
                        print("是读图片的时候了！")
                        base64_image = encode_image("received_image.jpg")
                        gpt_photo_reply = GPT_photo_and_language(base64_image=base64_image, question=gpt_reply_dic["意图"])
                        mq_gpt_to_car15_read.send_text(gpt_photo_reply)
                        
                    elif gpt_reply_dic["楼层"] == "16楼":
                        if gpt_reply_dic["二级地点"] != "无":
                            location2 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["二级地点"])
                            mq_gpt_to_car16_move.send_text(location2)
                        elif gpt_reply_dic["一级地点"] != "无":
                            location1 = next(item["location"] for item in locations if item["位置"] == gpt_reply_dic["一级地点"])
                            mq_gpt_to_car16_move.send_text(location1)
                        start_time = time.time()
                        while True:
                            mq_find_sys_to_car16.connect()
                            mq_find_sys_to_car16.send_text('look')
                            print("send to 16")
                            if time.time() - start_time > 2:
                                break  # 超时后退出循环
                            time.sleep(1)
                        while not os.path.isfile("received_image.jpg"):
                            pass
                        print("是读图片的时候了！")
                        base64_image = encode_image("received_image.jpg")
                        gpt_photo_reply = GPT_photo_and_language(base64_image=base64_image, question=gpt_reply_dic["意图"])
                        mq_gpt_to_car15_read.send_text(gpt_photo_reply)
                else: # 行为为无法完成时，即去一些不存在的点位
                    print("行为无法完成")
                        
        time.sleep(1)

def find_car15_to_sys():
    mq_find_car15_to_sys.connect()
    mq_find_car15_to_sys.channel.basic_consume(queue=mq_find_car15_to_sys.queue, on_message_callback=mq_find_car15_to_sys.callback_image, auto_ack=True)
    mq_find_car15_to_sys.channel.start_consuming()

def find_car16_to_sys():
    mq_find_car16_to_sys.connect()
    mq_find_car16_to_sys.channel.basic_consume(queue=mq_find_car16_to_sys.queue, on_message_callback=mq_find_car16_to_sys.callback_image, auto_ack=True)
    mq_find_car16_to_sys.channel.start_consuming()
        
if __name__ == "__main__":
    try:
        os.remove("received_image.jpg")
    except:
        print("文件已经清理完毕")

    t1 = threading.Thread(target=sys_to_car15)
    t1.start()
    t2 = threading.Thread(target=sys_to_car16)
    t2.start()
    t3 = threading.Thread(target=find_car15_to_sys)
    t3.start()
    t4 = threading.Thread(target=find_car16_to_sys)
    t4.start()

