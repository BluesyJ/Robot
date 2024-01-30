import openai
import re


from new_knowledge.lib_tcp import *



def extract_content_with_brackets(sentence):
    # 使用正则表达式匹配中括号[]中的内容
    match = re.search(r'\[([^]]+)\]', sentence)

    # 如果匹配到内容，返回中括号中的内容；否则返回None
    if match:
        return '['+match.group(1)+']'
    else:
        return None

def openai_reply(messages, apikey):
    openai.proxy = 'http://127.0.0.1:7890'
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

def ask_for_GPT(text_input = None, ord_tcp = None, voice_tcp = None, host = None):
    def send2read(read_text):
        ord_tcp.send_str(host, read_text)
        ord_tcp.wait()
    def ord2ord_list(ord):
        ord = eval(ord)
        ord_list = []
        ord_list2 = []
        locations = [{"name": "厨房","location": "{'x': -1.356573771429246, 'y': 4.999944688176971, 'yaw': 0.7946730148562868, 'z': 0.0}"},
                     {"name": "卧室","location": "{'x': -0.2218969712949318, 'y': -0.2515860317008285, 'yaw': -0.02445899149751707, 'z': 0.0}"},
                     {"name": "客厅","location": "{'x': -1.170713179748654, 'y': 0.04374214671541992, 'yaw': -2.255652161020206, 'z': 0.0}"},
                     {"name": "办公室", "location": "{'x': 0.5901472270676184, 'y': 2.874371793727706, 'yaw': 1.185127366482732, 'z': 0.0}"}]
        i = 0
        while i < len(ord):
            if ord[i] in ['go', 'reach', 'put', 'find']:
                # 如果当前元素是'go'、'reach'或者'put'，将它和下一个元素合成一个列表元素
                combined_element = [ord[i], ord[i + 1]]
                ord_list.append(combined_element)
                i += 2  # 跳过下一个元素
            elif ord[i] in ['catch', 'release']:
                # 如果当前元素是'catch'或者'release'，将它单独加入ord_list
                ord_list.append([ord[i]])
                i += 1  # 跳过下一个元素
            else:
                # 对于其他情况，将元素单独加入ord_list
                ord_list.append([ord[i]])
                i += 1
        print(ord_list)
        for i in ord_list:
            if i[0] in [ 'reach', 'put', 'catch', 'release']:
                ord_list2.append({'指令': '机械臂操作', '动作流程': str(i)})
            elif i[0] in ['go']:
                for loc in locations:
                    if loc["name"] in i[1]:
                        location = loc["location"]
                ord_list2.append({'指令': '移动', '目的地': i[1], '目的地坐标': str(location)})
            elif i[0] in ['find']:
                ord_list2.append({'指令': '找人', '目标': i[1]})
        return ord_list2
    messages = [
        {"role": "system", "content": "你是一位优秀的助手。"},
        {"role": "user", "content": "你是一个编写机器人基元执行指令的管家。"
                                    "现在我有一个机械臂，能够执行拿起['reach','somewhere','catch']、放到['put','somewhere','release']、拿到['put','somewhere']三个操作，"
                                    "机械臂能够拿起的东西有杯子和茶包，能够去的地方有茶包的位置['chabao'],杯子的位置['cup'],饮水机的位置['water'],托盘位置['tuopan'],"
                                    "还有一个移动机器人，能够执行去到['go','somewhere']的操作和['find','someone']，能够去到的位置有客厅['客厅']和厨房['厨房']和卧室['卧室']的位置,能找的人有['小明']和['小红']。"
                                    "比如说对于“泡茶”的任务，任务解析的语言描述为："
                                    "移动机器人去到厨房位置，机械臂拿起茶包放到杯子里，机械臂把杯子拿到饮水机下，等饮水机接水，机械臂把杯子放到托盘上，移动机器人去客厅；"
                                    "对应的基元执行指令为['go','厨房','reach','chabao','catch','put','cup','release','reach','cup','catch','put','water','put','tuopan','release','go','客厅']这个语言描述。"
                                    "比如说对于'找到小明'或者'东西给小明'的任务，解析的语言描述为："
                                    "移动机器人寻找小明；"
                                    "对应的基元执行指令为['find','小明']"
                                    "现在我需要你根据我接下来的任务，首先根据你的常识生成任务解析的语言描述并用非常简洁通俗的语言告诉我，尽量少说话，得到我的确认之后再生成基元指令给我。"},
        {"role": "assistant", "content": "好的，我明白了。请告诉我你的任务。"},
    ]
    if text_input != None:
        messages.append({"role": "user", "content": text_input})
        assistant_reply = openai_reply(messages, "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")
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
        send2read(assistant_reply)
    while True:
        user_reply,_ = voice_tcp.wait()
        messages.append({"role": "user", "content": user_reply})
        assistant_reply = openai_reply(messages,"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")
        messages.append({"role": "assistant", "content": assistant_reply})
        order = extract_content_with_brackets(assistant_reply)
        print(assistant_reply)
        if order == None:
            send2read(assistant_reply)
        else:
            send2read("好的，我将为您进行服务。")
            print(order)
            break
    print(ord2ord_list(order))
    return ord2ord_list(order)






if __name__ == '__main__':
    ask_for_GPT()
