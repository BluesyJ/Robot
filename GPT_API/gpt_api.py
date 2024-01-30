import openai
import re


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

def ask_for_GPT():

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

    while True:
        user_reply = input("输入:")
        print(user_reply)
        messages.append({"role": "user", "content": user_reply})
        assistant_reply = openai_reply(messages,"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")
        messages.append({"role": "assistant", "content": assistant_reply})
        print(assistant_reply)







if __name__ == '__main__':
    ask_for_GPT()

