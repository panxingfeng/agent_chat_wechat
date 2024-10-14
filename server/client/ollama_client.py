import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""
    def __init__(self, content):
        self.content = content

class OllamaClient:
    def __init__(self, model_name, ollama_url):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.headers = {"Content-Type": "application/json"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.RequestException)),
    )
    def invoke(self, message):
        llama_data = {
            "model": self.model_name,
            "messages": message,
            "stream": False
        }

        response = requests.post(self.ollama_url, json=llama_data, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        content = response.json().get('message', {}).get('content', '无法生成内容').strip()
        return ResponseWrapper(content) 
