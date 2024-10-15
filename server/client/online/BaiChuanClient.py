import json

import requests
from openai import OpenAI

from config.config import BAICHUAN_DATA


class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""

    def __init__(self, content):
        self.content = content


class BaiChuanClient:
    """
    调用百川大模型，模型的配置信息在config/config.py中，不支持设置自定义提示词
    示例模板: messages = [
        {"role": "user", "content": message}
    ]
    """
    def __init__(self, key=BAICHUAN_DATA.get("key"), url=BAICHUAN_DATA.get("url")):
        self.key = key
        self.url = url
        self.client = OpenAI(
            api_key=key,
            base_url=url,
        )

    def invoke(self, messages):
        client = OpenAI(
            api_key=BAICHUAN_DATA.get("key"),
            base_url="https://api.baichuan-ai.com/v1/",
        )
        completion = client.chat.completions.create(
            model="Baichuan2-Turbo",
            messages=messages,
            temperature=0.3,
            stream=False
        )
        return ResponseWrapper(completion.choices[0].message.content)


# 测试示例
if __name__ == "__main__":
    client = BaiChuanClient()
    prompt = BAICHUAN_DATA.get("prompt")
    message = "你是谁"
    messages = [
        {"role": "user", "content": message}
    ]

    response = client.invoke(messages)

    print(response.content)
