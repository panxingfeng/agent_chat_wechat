from config.config import OLLAMA_DATA
from config.templates.data.bot import RAG_PROMPT_TEMPLATE
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient

# 初始化 Ollama 客户端
client = OllamaClient()
client_ollama = client.get_client()

class OllamaModel:
    """
    使用 ollama 客户端部署的模型 来生成对话回答。
    """

    def __init__(self) -> None:
        """
        初始化 ollama 模型客户端。
        """
        self.client = client_ollama

    def chat(self, prompt: str, history=None, content=None) -> str:
        """
        使用 Ollama 生成回答。
        :param prompt: 用户的提问
        :param history: 对话历史
        :param content: 可参考的上下文信息
        :return: 生成的回答
        """
        if content is None:
            content = []
        if history is None:
            history = []
        full_prompt = RAG_PROMPT_TEMPLATE['PROMPT_TEMPLATE'].format(question=prompt, history=history, context=content)

        response = self.client.chat.completions.create(
            model=OLLAMA_DATA.get("model"),
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )

        # 返回模型回答
        return response.choices[0].message.content
