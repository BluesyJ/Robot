import openai
import re
import ast
import yaml

import socket
import os
import sys
import struct
from new_knowledge.lib_tcp import *
from GPT_API.GPT_photo import *
with open(r'C:\Users\Administrator\Desktop\机器人框架v2\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)
OpenAI_API_Key = config['car_knowledge']['OpenAI_API_Key']
with open(r'C:\Users\Administrator\Desktop\机器人框架v2\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config_guanyan5 = yaml.safe_load(config_file)
locations = config_guanyan5['car_knowledge']['locations']



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
    print(22222222222222222222222222222222222222)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.bind(('127.0.0.1', 8001))
        s.bind(('192.168.1.100', 8001))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    print("Wait for Connection.....................")

    # while True:
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
            new_filename = os.path.join(r'D:/UserFiles/文件/研究生/工作项目/机器人框架v2/GPT_API/' + fn)  # 在服务器端新建图片名（可以不用新建的，直接用原来的也行，只要客户端和服务器不是同一个系统或接收到的图片和原图片不在一个文件夹下）

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




def openai_reply(messages, apikey):
    openai.proxy = 'http://127.0.0.1:51081'
    openai.api_key = apikey
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # print(response)
    return response.choices[0].message.content


def normal_chat_with_GPT(text_input=None, ord_tcp=None, voice_tcp=None, host=None):
    def send2read(read_text):
        ord_tcp.send_str(host, read_text)
        ord_tcp.wait()

    def extract_dict(s):
        # 使用正则表达式匹配字典
        dict_pattern = r"\{.*?\}"
        matches = re.findall(dict_pattern, s)
        # 将找到的字符串转换为字典
        dicts = []
        for match in matches:
            try:
                # 使用ast.literal_eval安全地评估字符串
                dict_obj = ast.literal_eval(match)
                if isinstance(dict_obj, dict):  # 确保是字典
                    dicts.append(dict_obj)
            except:
                pass
        return dicts[0]

    messages = [
        {"role": "system", "content": "你是一位优秀的助手。"},
        {"role": "user", "content": "你好，你现在是一个家庭管家，负责主人日常生活的管理，"
                            "由于你的回答需要转语音再播放，所以你的回答需要尽可能的简短，最好一句话完成回答，并且在回答完后询问是否还有问题。你的回答只有以下四种选择："
                            "1.如果人是在询问问题，那你就正常回答问题。"
                            "2.我们的居家场景里面有两个位置：['客厅', '厨房']"
                            "如果问题涉及到这其中的地点的详细情况，"
                            "比如说去厨房看看饭好了吗，那你就只回答{'地点':'厨房', '问题': '看看饭好了吗'}，"
                            "再比如说有客人在吗，那你就只回答{'地点':'客厅', '问题': '有客人在吗'}，"
                            "但是如果语言中的位置不在所属的几个位置里面，比如说“一号位置是用来干嘛的”，那你就回答“没有您说的这个位置”"
                            "3.如果学生说的意思是没有问题了，你就只回答四个字：退出交流，"
                            "3.如果给你的语言并没有让你做什么或者问你什么，而是没有逻辑意义的语言，那说明可能麦克风收到了杂音，你就回答两个字：收到噪音。"},
        {"role": "assistant", "content": "你好！我将尽力以简洁的语言回答你的问题。请随时提问。"}, ]
    if text_input != None:
        messages.append({"role": "user", "content": text_input})
        assistant_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
        if "收到噪音" in assistant_reply:
            return None
        elif "地点" in assistant_reply and '问题' in assistant_reply and '{' in assistant_reply:
            reply_dic = extract_dict(assistant_reply)
            desired_location = next(item["location"] for item in locations if item["位置"] == reply_dic['地点'])
            ord_tcp.send_str(host, desired_location)
            # 输入操作
            # print("移动位置中")
            # send_string_to_server('192.168.1.109', 8888,desired_location)
            # print("传输图片中")
            # socket_service_image()
            # print("询问gpt")
            # gpt_photo_reply = GPT_photo_and_language(image_path = r'D:/UserFiles/文件/研究生/工作项目/机器人框架v2/GPT_API/image1.jpg', question = reply_dic['问题'])
            # print(gpt_photo_reply)
            # send2read(gpt_photo_reply)
            return None
        else:
            send2read(assistant_reply)
    while True:
        print('在GPT里！')
        user_reply, _ = voice_tcp.wait()
        messages.append({"role": "user", "content": user_reply})
        assistant_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
        if "退出交流" in assistant_reply:
            break
        elif "收到噪音" in assistant_reply:
            break
        elif "地点" in assistant_reply and '问题' in assistant_reply and '{' in assistant_reply:
            reply_dic = extract_dict(assistant_reply)
            desired_location = next(item["location"] for item in locations if item["位置"] == reply_dic['地点'])
            ord_tcp.send_str(host, desired_location)
            ord_tcp.wait()
            # 输入操作
            # print("移动位置中")
            # send_string_to_server('192.168.1.109', 8888,desired_location)
            # print("传输图片中")
            # socket_service_image()
            # print("询问gpt")
            # gpt_photo_reply = GPT_photo_and_language(image_path = r'D:/UserFiles/文件/研究生/工作项目/机器人框架v2/GPT_API/image1.jpg', question = reply_dic['问题'])
            # print(gpt_photo_reply)
            # send2read(gpt_photo_reply)
            return None
        else:
            send2read(assistant_reply)


def computer_normal_chat_with_GPT():
    messages = [
        {"role": "system", "content": "你是一位优秀的助手。"},
        {"role": "user", "content": "你好，你现在是一个教学系统的辅助机器人，教学系统负责教导学生一些实验流程，"
                                    "而实验流程以外的一些问题则会转接到你这里，由你来回答，"
                                    "由于你的回答需要转语音再播放，所以你的回答需要尽可能的简短，最好一句话完成回答，并且在回答完后询问是否还有问题。你的回答只有以下四种选择："
                                    "1.如果学生是在询问问题，那你就正常回答问题。"
                                    "2.我们的教学场景里面有七个位置：['一号位置', '二号位置', '三号位置', '四号位置', '五号位置', '六号位置', '黑板', '讲台']"
                                    "如果问题涉及到这其中的地点的详细情况并且你也无法观测，"
                                    "比如说去二号位置看看有没有人，那你就只回答{'地点':'二号位置', '问题': '看看有没有人'}，"
                                    "再比如说讲台上有人吗，那你就只回答{'地点':'讲台', '问题': '有人吗'}，"
                                    "再比如说四号位置的人在干嘛，那你就只回答{'地点':'四号位置', '问题': '人在干嘛'}"
                                    "但是如果语言中的位置不在所属的几个位置里面，比如说“以后位置是用来干嘛的”，那你就回答“没有您说的这个位置”"
                                    "3.如果学生说的意思是没有问题了，你就只回答四个字：退出交流，"
                                    "3.如果给你的语言并没有让你做什么或者问你什么，而是没有逻辑意义的语言，那说明可能麦克风收到了杂音，你就回答两个字：收到噪音。"},
        {"role": "assistant", "content": "你好！我将尽力以简洁的语言回答你的问题。请随时提问。"}, ]
    while True:
        user_reply = input("shuru")
        messages.append({"role": "user", "content": user_reply})
        assistant_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
# computer_normal_chat_with_GPT()