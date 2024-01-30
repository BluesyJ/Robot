import pika
import base64
# RabbitMQ连接信息
rabbitmq_host = '211.136.224.67'  # RabbitMQ服务器地址
rabbitmq_port = 30028  # RabbitMQ服务器端口
rabbitmq_vhost = '/'  # 虚拟主机
rabbitmq_user = 'guest'  # 用户名
rabbitmq_password = 'xidian123'  # 密码

# 创建RabbitMQ连接
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=rabbitmq_host,
    port=rabbitmq_port,
    virtual_host=rabbitmq_vhost,
    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='image_queue')

# 读取图片并编码为Base64
with open('1.jpg', 'rb') as image_file:  # 替换成您的图片路径
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# 发送图片路径到队列
channel.basic_publish(exchange='',
                      routing_key='image_queue',
                      body=image_data)
print(f"Sent image data")

# 关闭连接
connection.close()
