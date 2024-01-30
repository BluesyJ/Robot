import tkinter as tk
from tkinter import scrolledtext
import threading
import openai
import time

class GPTChat:
    def __init__(self, api_key):
        self.messages = [
            {"role": "system", "content": "你是一位优秀的助手。"},
        ]
        self.stop_thread = False
        self.api_key = api_key

    def get_gpt_response(self, user_input):
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=self.messages,
            temperature=0,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response.choices[0].message.content

    def chat_loop(self):
        while not self.stop_thread:
            user_input = input("用户输入:")  # 替换为Tkinter的Entry小部件
            self.messages.append({"role": "user", "content": user_input})
            assistant_reply = self.get_gpt_response(user_input)
            self.messages.append({"role": "assistant", "content": assistant_reply})
            time.sleep(1)

class DisplayChatWindow:
    def __init__(self, root, chat_instance):
        self.root = root
        self.root.title("GPT 中文聊天显示")
        self.chat_instance = chat_instance

        self.text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("SimSun", 12))  # 使用宋体字体
        self.text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # 在单独的线程中启动聊天循环
        chat_thread = threading.Thread(target=self.update_display)
        chat_thread.start()

    def update_display(self):
        while not self.chat_instance.stop_thread:
            chat_history = self.chat_instance.messages
            display_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in chat_history)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, display_text)
            self.text_widget.yview(tk.END)
            time.sleep(1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    api_key = "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"
    chat_instance = GPTChat(api_key)

    # 在单独的线程中启动聊天循环
    chat_thread = threading.Thread(target=chat_instance.chat_loop)
    chat_thread.start()

    root = tk.Tk()
    window = DisplayChatWindow(root, chat_instance)

    try:
        window.run()
    except KeyboardInterrupt:
        chat_instance.stop_thread = True
        chat_thread.join()

# 你是一个编写机器人基元执行指令的管家。现在我有一个机械臂，能够执行拿起[reach,somewhere,catch]、放到[put,somewhere,release]、拿到[put,somewhere]三个操作，机械臂能够拿起的东西有杯子和茶包，能够去的地方有茶包的位置[chabao],杯子的位置[cup],饮水机的位置[water],托盘位置[tuopan],还有一个移动机器人，能够执行去到[go,somewhere]的操作，能够去到的位置有客厅[room]和机械臂[arm]的位置。比如说对于“泡茶”的任务，任务解析的语言描述为：移动机器人去到机械臂位置，机械臂拿起茶包放到杯子里，机械臂把杯子拿到饮水机下，等饮水机接水，机械臂把杯子放到托盘上，移动机器人去客厅；对应的基元执行指令为[go,arm,reach,chabao,catch,put,cup,release,reach,cup,catch,put,water,put,tuopan,release,go,room]这个语言描述。现在我需要你根据我接下来的任务，首先根据你的常识生成任务解析的语言描述并告诉我，得到我的确认之后再生成基元指令给我。