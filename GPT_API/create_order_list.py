import openai
import re

def openai_reply(content, apikey):
    openai.proxy = 'http://127.0.0.1:7890'
    openai.api_key = apikey
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # gpt-3.5-turbo-0301
        messages=[
            {"role": "user", "content": content}
        ],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # print(response)
    return response.choices[0].message.content

def str2list(input_string):
    # 通过正则表达式提取列表
    pattern = r"\(([^)]+)\)"
    matches = re.findall(pattern, input_string)
    # 新的列表，用于存储单独的字符串
    new_list = []
    # 处理提取的元素
    for match in matches:
        elements = [elem.strip() for elem in match.split(',')]
        new_list.extend(elements)
    # 打印结果
    #print(new_list)
    return new_list

if __name__ == '__main__':
    instruction = "已知我有一个机械臂，定义有如下几个动作基元：(reach,somewhere)：机械臂移动到某个地方、(catch)：机械臂原地抓紧、(put,somewhere)：机械臂抓着物品移动到另一个地方、(release)：机械臂原地松手。举个例子：桌面上有茶包，杯子，饮水机，托盘，对于拿茶包放进杯子然后把杯子放饮水机上等接完水把杯子放托盘上的泡茶这个场景，逻辑顺序应该如下：[(reach,茶包位置),(catch),(put,杯子位置),(release),(reach,杯子位置),(catch),(put,饮水机位置),(release),(reach,杯子位置),(catch),(put,托盘位置),(release)]。接下来根据我的描述，生成一个动作基元的顺序列表返回给我，不要有描述以外多余的动作，不要创造描述以外的位置："
    sentence = "桌面上有茶包、杯子和书和饮水机，对应位置为chabao,cup,book,water。"
    ord = "把茶包放到书上，把杯子放到饮水机上。"
    content = instruction + sentence + ord
    ans = openai_reply(content, "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")
    print(ans)
    print(str2list(ans))

