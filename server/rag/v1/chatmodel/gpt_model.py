from config.config import CHATGPT_DATA
from config.templates.data.bot import RAG_PROMPT_TEMPLATE
from openai import OpenAI


class ChatGPTModel:
    """
    使用 OpenAI 来生成对话回答。
    """

    def __init__(self) -> None:
        """
        初始化 gpt 模型客户端。
        """
        self.client = OpenAI(
            api_key=CHATGPT_DATA.get("key"),
            base_url=CHATGPT_DATA.get("url")
        )

    def chat(self, prompt: str, history=None, content: str = '') -> str:
        """
        使用 gpt 生成回答。
        :param prompt: 用户的提问
        :param history: 对话历史
        :param content: 参考的上下文信息
        :return: 生成的回答
        """
        if history is None:
            history = []
        full_prompt = RAG_PROMPT_TEMPLATE.get('prompt_template').format(question=prompt, history=history, context=content)

        response = self.client.chat.completions.create(
            model=CHATGPT_DATA.get("model"),
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )

        # 返回模型回答
        return response.choices[0].message.content
