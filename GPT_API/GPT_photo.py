import base64
import requests
import os
import yaml

with open(r'C:\Users\Administrator\Desktop\机器人框架v2\config_guanyan5.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)
OpenAI_API_Key = config['car_knowledge']['OpenAI_API_Key']
os.environ["http_proxy"] = 'http://127.0.0.1:51081'
os.environ["https_proxy"] = 'http://127.0.0.1:51081'

import time 
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def GPT_photo_and_language(question = "图片里面有几个人,回我有几个即可，简练一点"):
    # Getting the base64 string
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OpenAI_API_Key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": question
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # response.json()
    return response.json()['choices'][0]['message']['content']

if __name__ == "__main__":
  image_path = "C:\\Users\\Administrator\\Desktop\机器人框架v2\\GPT_API\\3.jpg"
  base64_image = encode_image(image_path)
  # base64_image = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsKDAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCAHgAoADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDxO3t9reZsarDWKR3SzeT8rfNtb/epYo03FE5/2Vq7JC81vnDVyq78kbTUJFWbS0Zl+TB/u1Ums0WYps3f7NbUlvIY1T/x6obq1jjZN6bdz/xfNStKKvFmsXy7owdS09Fut424/vfdpLfT0eb7jbf9mtnUrWRpN/yqrfe20yztdr7HSqScupbp8vUyrzS0kXy3"
  
  a = time.time()
  print(GPT_photo_and_language())
  b = time.time()
  print(b-a)
