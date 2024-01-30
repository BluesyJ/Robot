from py2neo import Graph, Node, Relationship
import socket
import json


class KnowledgeBase(object):
    def __init__(self, knowledgebase_name):
        """
        参数:

        """
        # 获取主机名
        self.host_name = socket.gethostname()
        # 获取本地IPv4地址
        self.local_ip = socket.gethostbyname(self.host_name)
        self.uri = "bolt://" + self.local_ip + ":7687"
        #self.uri = "bolt://localhost:7687"
        self.username = "neo4j"
        self.password = "12345678"
        self.knowledgebase_name = knowledgebase_name
        self.graph = Graph(self.uri, auth=(self.username, self.password), name=self.knowledgebase_name)
        self.created_nodes = {}  # 用于存储已创建的节点，以便后续关系创建使用

    def creat_greph(self, graph_data):
        # 删除所有节点和关系
        self.graph.delete_all()
        print("已删除原有数据。")

        # 从 JSON 文件读取图谱数据
        with open(graph_data, "r") as json_file:
            graph_data = json.load(json_file)

        # 创建节点
        for node_data in graph_data["nodes"]:
            # print(node_data)
            node_id = node_data["id"]
            node_type = node_data["type"]
            node_name = node_data["name"]
            node_props = {key: value for key, value in node_data.items() if
                          key not in ["id", "type", "name"]}  # 提取除id、type、name之外的属性
            node_node = Node(node_type, name=node_name, id=node_id, **node_props)  # 将属性动态传递给Node对象
            self.graph.create(node_node)
            self.created_nodes[node_id] = node_node  # 将节点存储到字典中

        # 创建关系
        for relationship in graph_data["relationships"]:
            from_node_id = relationship["from"]
            to_node_id = relationship["to"]
            relation_type = relationship["type"]
            relation_props = {key: value for key, value in relationship.items() if
                              key not in ["from", "to", "type"]}  # 提取除from、to、type之外的属性

            from_node = self.created_nodes.get(from_node_id)  # 获取已创建的节点
            to_node = self.created_nodes.get(to_node_id)  # 获取已创建的节点

            if from_node and to_node:
                relation = Relationship(from_node, relation_type, to_node, **relation_props)
                self.graph.create(relation)
            else:
                print(f"关系创建失败：{from_node_id} -> {to_node_id}")

        print("知识图谱已成功构建。")

    def search_nodes_by_property(self, property_name, property_value):
        """
        在Neo4j图谱中
        输入你要查询的一对属性及其属性值，输出满足这个属性的所有实体，类型为list
        """
        query = f"""
        MATCH (n)
        WHERE n.{property_name} = $property_value
        RETURN n
        """
        result = self.graph.run(query, property_value=property_value)

        nodes = []
        for record in result:
            node = record["n"]
            nodes.append(dict(node))

        return nodes

    def get_entity_relationships(self, node_id):
        """
        查询Neo4j图谱中节点的所有关系
        :param node_id: 节点的唯一标识id
        :return: 包含关系信息的列表，每个关系是一个字典，包括起始节点ID、结束节点ID和关系类型
        """
        query = f"""
        MATCH (n)-[r]-(m)
        WHERE n.id = '{node_id}' OR m.id = '{node_id}'
        RETURN n, r, m
        """

        results = self.graph.run(query)
        node_relationships = []
        unique_relationships = set()  # 用于存储已添加的关系，避免重复添加

        for record in results:
            start_node = record["n"]
            end_node = record["m"]
            relationship = record["r"]
            # 判断关系是否已经被添加，避免重复添加
            if relationship.identity not in unique_relationships:
                start_node_id = start_node["id"]
                end_node_id = end_node["id"]
                node_relationships.append({
                    "start_node_id": start_node_id,
                    "end_node_id": end_node_id,
                    "relationship_type": type(relationship).__name__
                })
                unique_relationships.add(relationship.identity)

        return node_relationships

    def add_node(self, node_data):
        """
        向Neo4j图中添加一个节点。

        :param node_properties: 包含新节点属性的字典。
        """
        node_id = node_data["id"]
        node_type = node_data["type"]
        node_name = node_data["name"]
        node_props = {key: value for key, value in node_data.items() if
                      key not in ["id", "type", "name"]}  # 提取除id、type、name之外的属性
        node_node = Node(node_type, name=node_name, id=node_id, **node_props)  # 将属性动态传递给Node对象
        self.graph.create(node_node)
        self.created_nodes[node_id] = node_node  # 将节点存储到字典中

    def delete_node(self, node_id):
        """
        从Neo4j图中删除一个节点。

        :param node_id: 要删除的节点的ID。
        """
        query = f"""
        MATCH (n) 
        WHERE n.id = '{node_id}' 
        DETACH DELETE n
        """
        self.graph.run(query)

    def add_relationship(self, from_node_id, to_node_id, relationship_type, relationship_props=None):
        """
        在Neo4j图中两个节点之间添加关系（边）。

        :param from_node_id: 起始节点的ID。
        :param to_node_id: 结束节点的ID。
        :param relationship_type: 关系的类型。
        :param relationship_props: 关系的属性，可选。
        """
        from_node = self.graph.nodes.match(id=from_node_id).first()
        to_node = self.graph.nodes.match(id=to_node_id).first()

        if from_node and to_node:
            relation = Relationship(from_node, relationship_type, to_node, **(relationship_props or {}))
            self.graph.create(relation)
        else:
            print(f"关系创建失败：{from_node_id} -> {to_node_id}")

    def delete_relationship(self, start_node_id, end_node_id, relationship_type):
        """
        在Neo4j图中删除两个节点之间的关系（边）。

        :param start_node_id: 起始节点的ID。
        :param end_node_id: 结束节点的ID。
        :param relationship_type: 关系的类型。
        """
        query = f"""
        MATCH (start)-[r:{relationship_type}]-(end)
        WHERE start.id = '{start_node_id}' AND end.id = '{end_node_id}'
        DELETE r
        """
        self.graph.run(query)


if __name__ == '__main__':
    neo4j_graph = KnowledgeBase("neo4j")
    neo4j_graph.creat_greph("graph_data_commonknowledge.json")

    # # 查询节点
    # property_name = "TYPE"
    # property_value = "Room"
    # print(neo4j_graph.search_nodes_by_property(property_name, property_value))
    #
    # # 查询节点的关系
    # a = neo4j_graph.get_entity_relationships("prospect")
    # print(a)
    #
    # # 添加一个节点
    # new_node_properties = {"id": "item_cup_white", "type": "Item", "name": "新节点", "颜色": "黑色", "所属": "小红"}
    # neo4j_graph.add_node(new_node_properties)
    #
    # # 删除一个节点
    # neo4j_graph.delete_node("item_cup_white")
    #
    # # 删除一条关系
    # neo4j_graph.delete_relationship("prospect", "item_apple", "CONTAINS")
    #
    # # 增加一条关系
    # neo4j_graph.add_relationship("prospect", "item_apple", "CONTAINS")