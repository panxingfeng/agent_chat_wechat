import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.config import OLLAMA_DATA


class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""

    def __init__(self, content):
        self.content = content


class OllamaClient:
    def __init__(self, model, url):
        self.model = model
        self.url = url
        self.headers = {"Content-Type": "application/json"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.RequestException)),
    )
    def invoke(self, messages):
        llama_data = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        response = requests.post(self.url, json=llama_data, headers=self.headers, timeout=10)
        response.raise_for_status()

        content = response.json().get('message', {}).get('content', '无法生成内容').strip()
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
