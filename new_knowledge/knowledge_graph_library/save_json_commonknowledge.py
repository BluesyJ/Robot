import json

# 构建图谱数据
graph_data = {
    "nodes": [
        #概念层级
        {"id": "knowledge base", "type": "concept", "name": "knowledge base"},
        {"id": "background", "type": "concept", "name": "background"},
        {"id": "prospect", "type": "concept", "name": "prospect"},
        #房间层级
        {"id": "room_office", "type": "Room", "name": "书房", "location": "{'x':0.38, 'y':2.41, 'z':94.05, 'yaw':3.14*0.55}", "TYPE": "Room"},
        {"id": "room_bedroom", "type": "Room", "name": "卧室", "location": "{'x':0.38, 'y':2.41, 'z':94.05, 'yaw':3.14*0.55}", "TYPE": "Room"},
        {"id": "room_kitchen", "type": "Room", "name": "厨房", "location": "{'x':0.38, 'y':2.41, 'z':94.05, 'yaw':3.14*0.55}", "TYPE": "Room"},
        #区域层级
        {"id": "office_table", "type": "region", "name": "桌子"},
        {"id": "office_chair", "type": "region", "name": "椅子"},
        {"id": "office_sofa", "type": "region", "name": "沙发"},
        {"id": "kitchen_table", "type": "region", "name": "桌子"},
        {"id": "bedroom_bed", "type": "region", "name": "床"},
        {"id": "bedroom_table", "type": "region", "name": "桌子"},
        #物品层级
        {"id": "item_apple", "type": "Item", "name": "苹果", "颜色": "红色", "所属": "小红"},
        {"id": "item_keyboard", "type": "Item", "name": "键盘", "颜色": "灰色", "所属": "小红"},
        {"id": "item_computer", "type": "Item", "name": "电脑", "颜色": "黑色", "所属": "小明"},
        {"id": "item_cup_green", "type": "Item", "name": "杯子", "颜色": "白色", "所属": "小明"},
        {"id": "item_cup_white", "type": "Item", "name": "杯子", "颜色": "黑色", "所属": "小红"},
        #功能层级
        {"id": "function_paocha", "type": "function", "name": "泡茶"},
        #地点层级
        {"id": "locationA", "type": "location", "name": "地点A", "location": "{'x':0.38, 'y':2.41, 'z':94.05, 'yaw':3.14*0.55}", "TYPE": "location"},
    ],
    "relationships": [
        #概念层级
        {"from": "knowledge base", "to": "background", "type": "CONTAINS"},
        {"from": "knowledge base", "to": "prospect", "type": "CONTAINS"},
        #背景关系
        {"from": "background", "to": "room_office", "type": "CONTAINS"},
        {"from": "background", "to": "room_kitchen", "type": "CONTAINS"},
        {"from": "background", "to": "room_bedroom", "type": "CONTAINS"},
        {"from": "room_bedroom", "to": "bedroom_bed", "type": "CONTAINS"},
        {"from": "room_bedroom", "to": "bedroom_table", "type": "CONTAINS"},
        {"from": "room_office", "to": "office_table", "type": "CONTAINS"},
        {"from": "room_office", "to": "office_chair", "type": "CONTAINS"},
        {"from": "room_office", "to": "office_sofa", "type": "CONTAINS"},
        {"from": "room_kitchen", "to": "kitchen_table", "type": "CONTAINS"},
        #前景关系
        {"from": "prospect", "to": "item_apple", "type": "CONTAINS"},
        {"from": "prospect", "to": "item_keyboard", "type": "CONTAINS"},
        {"from": "prospect", "to": "item_computer", "type": "CONTAINS"},
        {"from": "prospect", "to": "item_cup_green", "type": "CONTAINS"},
        {"from": "prospect", "to": "item_cup_white", "type": "CONTAINS"},
        #功能地点关系
        {"from": "function_paocha", "to": "locationA", "type": "at"},
    ]
}

# 将图谱数据保存为 JSON 文件
with open("graph_data_commonknowledge.json", "w") as json_file:
    json.dump(graph_data, json_file, indent=4)

print("图谱数据已保存。")
