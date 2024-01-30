import openai
import re
import networkx as nx
import matplotlib.pyplot as plt

def openai_reply(content, apikey):
    openai.api_key = apikey
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",  # gpt-3.5-turbo-0301
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



if __name__ == '__main__':
    instruction = "对下面句子使用自然语言做命名实体抽取,抽取实体类型为{'人类','组织','影视作品','书籍'}，注意只能抽取我给出的类型的实体，其他的实体全部丢弃，考虑上下文和常规含义，以确保实体的含义能够归类为其类型，以(实体,类型)的形式回答。"
    sentence = "《红楼梦》是中央电视台和中国电视剧制作中心根据中国古典文学名著《红楼梦》摄制于1987年的一部古装连续剧，由王扶林导演，周汝昌、王蒙、周岭等多位红学家参与制作。"
    content = instruction + sentence
    ans = openai_reply(content, "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")
    print(ans)

