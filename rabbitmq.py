import pika
import base64
import time
class MQUnit:
    def __init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_vhost, rabbitmq_user, rabbitmq_password, queue):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_vhost = rabbitmq_vhost
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_password = rabbitmq_password
        self.queue = queue

        self.connection = None
        self.channel = None


    # producer
    def send_image(self, image_path):
        # 读取图片并编码为Base64
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # 发送图片数据到队列
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   body=image_data)
        print("Sent image")

    def send_text(self, text):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   body=text)
        # print('send text')


    #consumer
    def callback_image(self, ch, method, properties, body):
        # 接收图片数据并保存
        image_data = base64.b64decode(body)
        filename = f"received_image.jpg"
        with open(filename, 'wb') as file:
            file.write(image_data)
        print(f"Saved image as {filename}")

    def callback_text(self, ch, method, properties, body):
        # 处理接收到的文本消息
        print(f"Received text message: {body.decode('utf-8')}")

        # # 判断是否达到最大消息数量
        # if self.message_count >= self.max_messages:
        #     print(f"Received {self.max_messages} messages. Exiting...")
        #     ch.stop_consuming()  # 停止消息接收


    #else
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
        self.channel.queue_declare(queue=self.queue)

    def clean(self, queue):
        self.connect()
        while True:
            method_frame, _, body = self.channel.basic_get(queue=queue, auto_ack=True)
            if method_frame:
                # 删除队列中的消息
                print(f"Deleted message: {body.decode('utf-8')}")
            else:
                break  # 队列为空时退出循环
        # self.close_connection()


    def close_connection(self):
            if self.connection:
                self.connection.close()


if __name__ == "__main__":
    mq_vqa_consumer = MQUnit('211.136.224.67', 30028, '/', 'guest', 'xidian123', "gpt_to_car15_move")
    mq_vqa_consumer.connect()
    while True:
        method_frame, header_frame, body = mq_vqa_consumer.channel.basic_get(queue=mq_vqa_consumer.queue, auto_ack=True)
        print("等待接收")
        if method_frame:
            # 处理消息
            print(f"Received message: {body.decode('utf-8')}")
        else:
            # 队列中没有新消息，可以执行其他操作或休眠一段时间
            time.sleep(1)
