from openai import OpenAI

from config.config import MOONSHOT_DATA

class ResponseWrapper:
    """包装API返回的响应内容，支持 .content 访问。"""

    def __init__(self, content):
        self.content = content


class MoonshotClient:
    """
    调用kimi大模型，模型的配置信息在config/config.py中
    示例模板: messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]
    """
    def __init__(self, key=MOONSHOT_DATA.get("key"), url=MOONSHOT_DATA.get("url")):
        self.key = key
        self.url = url
        self.client = OpenAI(
            api_key=key,
            base_url=url,
        )

    def invoke(self, messages):
        completion = self.client.chat.completions.create(
            model=MOONSHOT_DATA.get("model"),
            messages=messages,
            temperature=0.3,
        )
        return ResponseWrapper(completion.choices[0].message.content)


# 测试示例
if __name__ == "__main__":
    client = MoonshotClient()
    prompt = MOONSHOT_DATA.get("prompt")
    message = "你是谁"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message}
    ]

    response = client.invoke(messages)

    print(response.content)
