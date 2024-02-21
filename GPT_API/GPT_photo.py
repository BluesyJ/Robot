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

def GPT_photo_and_language(base64_image = "", question = ""):
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
  image_path = "received_image.jpg"
  base64_image = encode_image(image_path)
  print(GPT_photo_and_language(base64_image=base64_image, question="图中有人吗"))
