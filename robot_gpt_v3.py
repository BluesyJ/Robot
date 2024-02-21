#coding:utf-8
import openai
import re
import ast
import yaml
from new_knowledge.lib_tcp import *
from GPT_API.GPT_photo import *
from rabbitmq import *

# 读取本地知识库
with open(r'C:\Users\Administrator\Desktop\机器人框架v2\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)
locations = config['car_knowledge']['locations']
OpenAI_API_Key = config['car_knowledge']['OpenAI_API_Key']

# 建立连接
mq_car15_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "car15_to_sys")
mq_car16_to_sys = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "car16_to_sys")
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

def normal_chat_with_GPT(text_input=None): # car用于判断是哪辆车请求调用GPT
    def extract_dict(s):
        # 将输入字符串格式化为字典格式的字符串
        formatted_str = "{" + s[1:-1].replace("':'", "': '") + "}"

        # 使用ast.literal_eval安全地评估字符串，并将其转换为字典
        try:
            result_dict = ast.literal_eval(formatted_str)
            return result_dict
        except SyntaxError as e:
            print(f"转换失败: {e}")
            return None

    messages = [
        {"role": "system", "content": "你是一位智能家居助手。"},
        {"role": "user", "content": "以下是场景信息的描述：\n"
         "下面是属于15楼的一级地点、二级地点、对象： 一级地点有：客厅、卧室、厨房； 二级地点有：冰箱(一级地点客厅里)、沙发(一级地点客厅里)、床(一级地点卧室里)、厨房台面(一级地点厨房里)； 对象有：电饭煲(二级地点厨房台面上)、张三(二级地点床上)。 下面是属于16楼的一级地点、二级地点、对象： 一级地点有：办公室； 二级地点有：办公桌(一级地点办公室里)； 对象有：电脑(二级地点办公桌上)。\n"
         "以下是你的几项子任务，每次回答你只能选择其中一种：\n"
         "任务一：如果人的话有清晰的目的性，是让你做出'观察'或者'移动'的，并且你认为这个任务设计的对象和地点在场景信息中有所以你能够做到，那么你就输出解析语言的意图、行为、一级地点、二级地点、对象。 任务二：如果人的话有清晰的目的，但是让你做出'观察'或者'移动'以外你不能做的事，或者观察不存在的对象、去到没有的地点，你就输出行为无法完成。 任务三：如果人的话没有清晰的目的性或者没有逻辑，可能不是对着你说的或者有噪音，你就输出意图为收到噪音。\n"
         "注意，你的描述应该言简意赅，尽量简短。\n下面是一些解析语言的例子：\n如果人跟你说的话是：张三在睡觉吗？，你的回答应该是：\n['意图':'判断张三是否在睡觉', '行为':'观察', '楼层':'15楼', '一级地点':'卧室', '二级地点':'床', '对象':'张三']\n如果人跟你说的话是：过来客厅呆着，你的回答应该是：\n['意图':'去客厅', '行为':'移动', '楼层':'15楼', '一级地点':'客厅', '二级地点':'无', '对象':'无']\n如果人跟你说的话是：过来办公室呆着，你的回答应该是：\n['意图':'去办公室', '行为':'无法完成', '楼层':'无', '一级地点':'无', '二级地点':'无', '对象':'无']\n如果人跟你说的话是：去床边上，你的回答应该是：\n['意图':'去床边', '行为':'移动', '楼层':'15楼', '一级地点':'卧室', '二级地点':'床', '对象':'无']\n如果人跟你说的话是：这是什么？，你的回答应该是：\n['意图':'收到噪音', '行为':'无', '楼层':'无', '一级地点':'无', '二级地点':'无', '对象':'无']\n如果人跟你说的话是：哈哈哈，喂，你的回答应该是：\n['意图':'收到噪音', '行为':'无', '楼层':'无', '一级地点':'无', '二级地点':'无', '对象':'无']\n如果人跟你说的话是：饭做好了吗？，你的回答应该是：\n['意图':'判断饭是否熟了', '行为':'观察', '楼层':'15楼', '一级地点':'厨房', '二级地点':'厨房台面', '对象':'电饭煲']\n如果人跟你说的话是：我的电脑关了吗？，你的回答应该是：\n['意图':'判断电脑是否关了', '行为':'观察', '楼层':'16楼', '一级地点':'办公室', '二级地点':'办公桌', '对象':'电脑']\n如果人跟你说的话是：电脑怎么样了，你的回答应该是：\n['意图':'判断电脑状态', '行为':'观察', '楼层':'16楼', '一级地点':'办公室', '二级地点':'办公桌', '对象':'电脑']\n如果人跟你说的话是：来办公桌旁边一下，你的回答应该是：\n['意图':'去办公桌旁边', '行为':'移动', '楼层':'16楼', '一级地点':'办公室', '二级地点':'办公桌', '对象':'无']\n如果人跟你说的话是：厨房的苹果在哪，你的回答应该是：['意图':'去厨房找苹果', '行为':'无法完成', '楼层':'无', '一级地点':'无', '二级地点':'无', '对象':'无']\n现在轮到你来解析了，下面是人跟你说的话:"
        }, ]
    if text_input != None:
        messages.append({"role": "user", "content": text_input})
        gpt_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": gpt_reply})
        print(gpt_reply)
        gpt_reply_dic = extract_dict(gpt_reply)
        if "收到噪音" in gpt_reply_dic:
            return None
        else:
            return gpt_reply_dic
        
if __name__ == "__main__":
    normal_chat_with_GPT("看看人睡着没？")