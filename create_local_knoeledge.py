import json

# 初始化地点信息知识库
location_knowledge_base = {}

def save_knowledge_base_to_json():
    # 将地点信息知识库保存为JSON文件
    with open('location_knowledge_base.json', 'w') as file:
        json.dump(location_knowledge_base, file, indent=4)

def load_knowledge_base_from_json():
    # 从JSON文件加载地点信息知识库
    global location_knowledge_base
    try:
        with open('location_knowledge_base.json', 'r') as file:
            location_knowledge_base = json.load(file)
    except FileNotFoundError:
        # 如果文件不存在，初始化一个空的知识库
        location_knowledge_base = {}

def add_location(name, coordinates):
    # 添加地点信息到知识库
    location_knowledge_base[name] = coordinates
    save_knowledge_base_to_json()

def remove_location(name):
    # 从知识库中删除地点信息
    if name in location_knowledge_base:
        del location_knowledge_base[name]
        save_knowledge_base_to_json()

def get_location_coordinates(name):
    # 获取地点的坐标信息
    return location_knowledge_base.get(name)

# 加载地点信息知识库
load_knowledge_base_from_json()

# 示例：添加地点信息
add_location('厨房', [{'x': -0.4279227344246886, 'y': -3.005830278585012, 'yaw': 0.4869387496727815, 'z': 0.0},
            {'x': -0.4355224645910675, 'y': -3.013407318145257, 'yaw': -0.409713681761728, 'z': 0.0}])

# 示例：获取地点坐标信息
kitchen_coordinates = get_location_coordinates('厨房')
print("厨房坐标信息:", kitchen_coordinates)

# 示例：删除地点信息
remove_location('客厅')

# 打印当前地点信息知识库
print("当前地点信息知识库:", location_knowledge_base)
