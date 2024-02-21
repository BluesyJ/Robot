
import re
import ast
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

s = "['意图':'收到噪音', '行为':'无', '楼层':'无', '一级地点':'无', '二级地点':'无', '对象':'无']"
print(type(s))
result = extract_dict(s)
print(result)