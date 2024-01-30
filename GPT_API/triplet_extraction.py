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

def drawgraph(triples):
    # 创建有向图
    G = nx.DiGraph()

    # 添加节点和边
    for triple in triples:
        subject, predicate, obj = triple
        G.add_edge(subject, obj, label=predicate)

    # 绘制图谱
    pos = nx.spring_layout(G)  # 定义节点布局
    labels = nx.get_edge_attributes(G, 'label')  # 获取边标签

    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定中文字体，例如微软雅黑或黑体
    plt.rcParams['axes.unicode_minus'] = False  # 用于显示负号
    plt.show()

if __name__ == '__main__':
    instruction = "使用自然语言抽取三元组,已知下列句子,请从句子中抽取出可能的实体、关系,抽取实体类型为{'专业','时间','人类','组织','地理地区','事件'},关系类型为{'制作组织','参加','国家','导演','地点','属于','获奖','时间'},你可以先识别出实体再判断实体之间的关系,以(头实体,关系,尾实体)的形式回答，注意必须只能以我给出的关系范围内回答。"
    sentence = "《红楼梦》是中央电视台和中国电视剧制作中心根据中国古典文学名著《红楼梦》摄制于1987年的一部古装连续剧，由王扶林导演，周汝昌、王蒙、周岭等多位红学家参与制作。"
    content = instruction + sentence
    ans = openai_reply(content, "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")
    print(ans)
    # 使用正则表达式提取每一组三元组
    triples = re.findall(r'\((.*?), (.*?), (.+?)\)', ans)

    # # 打印提取的结果
    # for triple in triples:
    #     subject, predicate, object = triple
    #     print(f"头实体: {subject}, 关系: {predicate}, 尾实体: {object}")

    drawgraph(triples)
