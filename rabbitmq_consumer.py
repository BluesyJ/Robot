import pika
import base64
import sys

if __name__ == "__main__":
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

    def callback(ch, method, properties, body):
        image_data = body
        print("Received image data")

        # 将Base64编码的文本数据还原为图片内容并保存到本地
        with open('received_image.jpg', 'wb') as file:
            file.write(base64.b64decode(image_data))
        print("Saved image as received_image.jpg")

        sys.exit(0)

    # 声明队列
    channel.queue_declare(queue='image_queue_syj')

    # 设置回调函数
    channel.basic_consume(queue='image_queue_syj', on_message_callback=callback, auto_ack=True)

    # 开始监听队列
    print('Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()
