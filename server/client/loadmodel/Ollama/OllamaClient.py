import requests
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.config import OLLAMA_DATA


class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""
    def __init__(self, content):
        self.content = content


class OllamaClient:
    """
    调用本地部署的ollama大模型，模型的配置信息在config/config.py中
    示例模板: messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]
    """
    def __init__(self, model, url):
        self.model = model
        self.url = url
        self.client = self.get_client()  # 调用 get_client 初始化

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.RequestException)),
    )

    def get_client(self):
        # 确保正确返回 OpenAI 实例
        return OpenAI(
            base_url=OLLAMA_DATA.get("api_url"),
            api_key='ollama',
        )

    def invoke(self, messages):
        print(dir(self.client))  # 打印所有可用属性
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
        )
        content = chat_completion.choices[0].message.content
        return ResponseWrapper(content)

# 测试示例
if __name__ == "__main__":
    client = OllamaClient(
        model=OLLAMA_DATA.get("model"),
        url=OLLAMA_DATA.get("url")
    )

    prompt = "你是一个乐于助人的助手"
    message = "简单讲述一下大语言模型"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]

    response = client.invoke(messages)

    print(response.content)
