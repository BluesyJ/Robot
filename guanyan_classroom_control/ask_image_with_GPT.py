import base64
import requests
import os

os.environ["http_proxy"] = "http://127.0.0.1:51081"
os.environ["https_proxy"] = "http://127.0.0.1:51081"

# OpenAI API Key
api_key = "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"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "1.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

# print(base64_image)
# print(type(base64_image))



def ask_image_with_GPT(base64_image): 
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": "这张图里有人吗？只回我有或没有"
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

    print(response.json())

if __name__ == "__main__":
    ask_image_with_GPT(base64_image=base64_image)