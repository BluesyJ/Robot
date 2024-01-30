from hanlp_restful import HanLPClient
import tkinter as tk
from tkinter import ttk
from car_voice.audionew import *
from car_voice.baidu_voice2text2words import *
import threading
from new_knowledge.lib_tcp import *
import yaml

with open(r'D:\UserFiles\文件\研究生\工作项目\机器人框架v2\config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)

item_loc = config['car_knowledge']['item_loc']
locations = config['car_knowledge']['locations']
HanLP_auth = config['car_knowledge']['HanLP_auth']
def display_instructions(data):
    # 创建一个窗口
    window = tk.Tk()
    window.title("指令")
    window.geometry("1000x200")  # 设置窗口大小
    # 创建一个列表框，设置字体和背景颜色
    listbox = tk.Listbox(window, font=("Helvetica", 16), bg="lightblue")
    listbox.pack(fill=tk.BOTH, expand=True)
    # 遍历字典，将内容显示在列表框中
    for d in data:
        item_text = ""
        for key, value in d.items():
            item_text += f"{key}: {value}, "
        item_text = item_text.rstrip(", ")  # 去掉末尾的逗号和空格
        listbox.insert(tk.END, item_text)
    # 运行窗口
    window.mainloop()

def get_ord_list(text):#收集指令
    if text == "":
        text = "无"
    # auth不填则匿名，zh中文，mul多语种
    HanLP = HanLPClient('https://www.hanlp.com/api', auth=HanLP_auth, language='zh')
    doc = HanLP.parse(text, tasks=['srl'])
    #print(doc)
    doc.pretty_print()
    ord_list = []
    for i, pas in enumerate(doc['srl'][0]):
        #print(f'第{i+1}个谓词论元结构：')
        ord_dic = {"受事者1": "None", "谓词": "None", "受事者2": "None", "受益者": "None"}
        for form, role, begin, end in pas:
            #print(f'{form} = {role} at [{begin}, {end})')
            if role == "ARG1" :
                ord_dic["受事者1"] = form
            elif role == "ARGM-BNF" :
                ord_dic["受益者"] = form
            elif role == "PRED" :
                ord_dic["谓词"] = form
            elif role == "ARG2" :
                ord_dic["受事者2"] = form
        ord_list.append(ord_dic)
    return ord_list

def charge_ord(list):#判断是什么类型的的指令
    new_list = []
    for i in list:
        if i["谓词"] == "泡茶" or i["谓词"] == "泡":
            i["指令"] = "泡茶"
            new_list.append(i)
        elif i["谓词"] == "消毒" or i["谓词"] == "消杀":
            i["指令"] = "消杀"
            new_list.append(i)
        elif i["谓词"] == "找" :
            i["指令"] = "寻物"
            new_list.append(i)
        elif i["谓词"] == "去" or i["谓词"] == "来" or i["谓词"] == "过来" or i["谓词"] == "到" or i["谓词"] == "送去":
            i["指令"] = "移动"
            new_list.append(i)
        elif i["谓词"] == "放到" or i["谓词"] == "放进" or i["谓词"] == "放在" or i["谓词"] == "拿起" or i["谓词"] == "拿" or i["谓词"] == "拿到" or i["谓词"] == "接":
            i["指令"] = "机械臂操作"
            new_list.append(i)
    return new_list

def handle_list(list):#处理指令成发送的内容
    global item_loc, locations
    new_list = []
    for i in list:
        instruct = {}
        #机械臂操作
        if i["指令"] == "机械臂操作":
            if i["受事者1"] != "None" and i["受事者2"] != "None":
                instruct["指令"] = "机械臂操作"
                for item in item_loc:
                    if item in i["受事者1"]:
                        arg1 = item
                    if item in i["受事者2"]:
                        arg2 = item
                # arg1 = i["受事者1"]
                # arg2 = i["受事者2"]
                instruct["动作流程"] = f"['reach', '{item_loc[arg1]}', 'catch', 'put', '{item_loc[arg2]}', 'release']"
            elif i["受事者1"] == "None" and i["受事者2"] != "None":
                instruct["指令"] = "机械臂操作"
                for item in item_loc:
                    if item in i["受事者2"]:
                        arg2 = item
                instruct["动作流程"] = f"['put', '{item_loc[arg2]}', 'release']"
            elif i["受事者1"] != "None" and i["受事者2"] == "None":
                instruct["指令"] = "机械臂操作"
                for item in item_loc:
                    if item in i["受事者1"] or i["受事者1"] in item:
                        arg1 = item
                    if item in i["受益者"] or i["受益者"] in item:
                        bnf = item
                if i["谓词"] == "拿到":
                    instruct["动作流程"] = f"['put', '{item_loc[arg1]}']"
                elif i["谓词"] == "接":
                    instruct["动作流程"] = f"['put', '{item_loc[arg1]}','dialog']"
                else:
                    if i["受益者"] == "None":
                        instruct["动作流程"] = f"['reach', '{item_loc[arg1]}', 'catch']"
                    else :
                        instruct["动作流程"] = f"['reach', '{item_loc[arg1]}', 'catch', 'put', '{item_loc[bnf]}', 'release']"
        #移动
        elif i["指令"] == "移动":
            instruct["指令"] = "移动"
            instruct["目的地"] = i["受事者1"]
            for loc in locations:
                if loc["name"] in i["受事者1"]:
                    instruct["目的地坐标"] = loc["location"]
        #寻物
        elif i["指令"] == "寻物":
            instruct["指令"] = "寻物"
            instruct["目标物品"] = i["受事者1"]
        #消杀
        elif i["指令"] == "消杀":
            instruct["指令"] = "消杀"
            instruct["消杀位置"] = i["受事者1"]
        #泡茶
        elif i["指令"] == "泡茶":
            instruct["指令"] = "泡茶"
            instruct["服务对象"] = i["受益者"]
        new_list.append(instruct)
    return new_list

if __name__ == '__main__':
    # 设置服务端地址和端口
    # arm_host = '192.168.3.36'  # 服务端主机地址
    # car_host = '192.168.3.17'  # 服务端主机地址
    # computer_host = '192.168.3.16'  # 服务端主机地址
    # audio = Audio()
    # tcp = TCP()
    while(1):
        # x = audio.get_info('UACDemoV1.0: USB Audio (hw:2,0)')
        # print(x)
        # audio.record()
        # read_text = get_baidu_text("D:/UserFiles/文件/研究生/工作项目/知识图谱/car_voice/change.wav")    #识别语音文件
        read_text = '把杯子放到托盘上'
        print(read_text)
        list1 = get_ord_list(read_text)
        for i in list1:
            print(i)
        list2 = charge_ord(list1)
        for i in list2:
            print(i)
        list3 = handle_list(list2)
        for i in list3:
            print(i)
            # if i["指令"] == "机械臂操作":
            #     tcp.send_str(arm_host,i["动作流程"])
            # elif i["指令"] == "移动":
            #     tcp.send_str(car_host, i["目的地坐标"])
            # tcp.wait()
        break
