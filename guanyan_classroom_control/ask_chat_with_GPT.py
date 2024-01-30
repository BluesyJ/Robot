import openai
import re
import yaml

with open(r'C:\Users\Administrator\Desktop\机器人框架v2\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)

OpenAI_API_Key = config['car_knowledge']['OpenAI_API_Key']

def openai_reply(messages, apikey):
    openai.proxy = 'http://127.0.0.1:51081'
    openai.api_key = apikey
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # print(response)
    return response.choices[0].message.content

def ask_chat_with_GPT(text_input = None, ord_tcp = None, voice_tcp = None, host = None):
    def send2read(read_text):
        ord_tcp.send_str(host, read_text)
        ord_tcp.wait()

    messages = [
        {"role": "system", "content": "你是一位优秀的助手。"},
        {"role": "user", "content": "你好，你现在是一个教学系统的辅助机器人，教学系统负责教导学生一些实验流程，"
                                    "而实验流程以外的一些问题则会转接到你这里，由你来回答，"
                                    "由于你的回答需要转语音再播放，所以你的回答需要尽可能的简短，最好一句话完成回答，并且在回答完后询问是否还有问题。"
                                    "如果学生说的意思是没有问题了，你就只回答四个字：退出交流"},
        {"role": "assistant", "content": "你好！我将尽力以简洁的语言回答你的问题。请随时提问。"}, ]
    if text_input != None:
        messages.append({"role": "user", "content": text_input})
        assistant_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
        send2read(assistant_reply)
    while True:
        user_reply, _ = voice_tcp.wait()
        messages.append({"role": "user", "content": user_reply})
        assistant_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
        if "退出交流" in assistant_reply:
            break
        send2read(assistant_reply)


def ask_normal_chat_with_GPT():
    messages = [
        {"role": "system", "content": "你是一位优秀的助手。"},
        {"role": "user", "content": "你好，你现在是一个教学系统的辅助机器人，教学系统负责教导学生一些实验流程，"
                                    "而实验流程以外的一些问题则会转接到你这里，由你来回答，"
                                    "由于你的回答需要转语音再播放，所以你的回答需要尽可能的简短，最好一句话完成回答，并且在回答完后询问是否还有问题。"
                                    "如果学生说的意思是没有问题了，你就只回答四个字：退出交流"},
        {"role": "assistant", "content": "你好！我将尽力以简洁的语言回答你的问题。请随时提问。"}, ]
    while True:
        user_reply = input("shuru")
        messages.append({"role": "user", "content": user_reply})
        assistant_reply = openai_reply(messages, OpenAI_API_Key)
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)
# ask_normal_chat_with_GPT()