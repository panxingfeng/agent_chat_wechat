import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class OllamaClient:
    def __init__(self, model_name, ollama_url):
        """
        初始化 OllamaClient 客户端。
        :param model_name: 使用的模型名称，例如 'qwen2.5'。
        :param ollama_url: Ollama API 的 URL。
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.headers = {
            "Content-Type": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),  # 最大重试 3 次
        wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数级退避等待时间
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.RequestException))
    )
    def run_ollama(self, message):
        """
        使用 Ollama API 生成回复内容，并支持重试机制。
        :param message: 用户输入的消息。
        :return: API 返回的内容或错误消息。
        """
        llama_data = {
            "model": self.model_name,
            "messages": message,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=llama_data, headers=self.headers, timeout=10)
        response.raise_for_status()  # 如果状态码不是 200，会抛出 HTTPError 异常
        return response.json().get('message', {}).get('content', '无法生成内容').strip()
