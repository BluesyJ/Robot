import pika
import base64
import sys

class MQConsumer:
    def __init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_vhost, rabbitmq_user, rabbitmq_password, queue_name):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_vhost = rabbitmq_vhost
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_password = rabbitmq_password
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.message_count = 0
        self.max_messages = 0

    def connect(self):
        # 创建RabbitMQ连接
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            virtual_host=self.rabbitmq_vhost,
            credentials=pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_password)
        ))
        self.channel = self.connection.channel()

        # 声明队列
        self.channel.queue_declare(queue=self.queue_name)

    def callback_image(self, ch, method, properties, body):
        # 接收图片数据并保存
        image_data = base64.b64decode(body)
        filename = f"received_image_{method.delivery_tag}.jpg"
        with open(filename, 'wb') as file:
            file.write(image_data)
        print(f"Saved image as {filename}")

    def callback_text(self, ch, method, properties, body):
        # 处理接收到的文本消息
        print(f"Received text message: {body.decode('utf-8')}")
        self.message_count += 1

        # 判断是否达到最大消息数量
        if self.message_count >= self.max_messages:
            print(f"Received {self.max_messages} messages. Exiting...")
            ch.stop_consuming()  # 停止消息接收
    
    def callback_voice(self, ch, method, properties, body):
        # 处理接收到的文本消息
        print(f"Received text message: {body.decode('utf-8')}")
        self.message_count += 1

        # 判断是否达到最大消息数量
        if self.message_count >= self.max_messages:
            print(f"Received {self.max_messages} messages. Exiting...")
            ch.stop_consuming()  # 停止消息接收

    def start_consuming(self):
        self.max_messages = 1
        # 设置回调函数
        if self.queue_name.startswith('image_'):
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback_image, auto_ack=True)
        elif self.queue_name.startswith('voice_'):
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback_text, auto_ack=True)

        else:
            raise ValueError("Queue name must end with '_image' or '_text' for proper message handling")

        # 开始监听队列
        print(f'Waiting for messages on queue "{self.queue_name}". To exit press CTRL+C')
        self.channel.start_consuming()

    def close_connection(self):
        if self.connection:
            self.connection.close()

if __name__ == "__main__":
    rabbitmq_host = '211.136.224.67'
    rabbitmq_port = 30028
    rabbitmq_vhost = '/'
    rabbitmq_user = 'guest'
    rabbitmq_password = 'xidian123'
    image_queue_name = 'image_queue'
    text_queue_name = 'gpt_to_car_read'
    # 创建一个消费者实例，用于接收文本消息
    text_consumer = MQConsumer(rabbitmq_host, rabbitmq_port, rabbitmq_vhost, rabbitmq_user, rabbitmq_password, text_queue_name)
    text_consumer.connect()

    try:
        # 启动文本消息消费者
        text_consumer.start_consuming()
    except KeyboardInterrupt:
        pass

    text_consumer.close_connection()
