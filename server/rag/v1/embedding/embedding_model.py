from typing import List

from openai import OpenAI

from config.config import OLLAMA_DATA, CHATGPT_DATA
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient

client = OllamaClient()
client_ollama = client.get_client()

gpt_client = OpenAI(
    api_key=CHATGPT_DATA.get("key"),
    base_url=CHATGPT_DATA.get("url")
)


class EmbeddingModel:
    """
    向量模型客户端
    """
    def __init__(self) -> None:
        """
        根据参数配置来选择ollama客户端还是GPT客户端
        """
        self.client = gpt_client if CHATGPT_DATA.get("use") else client_ollama

    def get_embedding(self, text: str) -> List[float]:
        """
        text (str) - 需要转化为向量的文本
        model_name (str) - ollama-使用的 ollama 的模型名称，“bge-m3”  gpt-使用的是默认的“text-embedding-3-small”
        
        return：list[float] - 文本的向量表示
        """
        if CHATGPT_DATA.get("use"):
            model = CHATGPT_DATA.get("embedding_model")
            # 去掉文本中的换行符，保证输入格式规范
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input=[text], model=model).data[0].embedding
        else:
            model = OLLAMA_DATA.get("embedding_model")
            if model == "" and OLLAMA_DATA.get("model") == "":
                # 如果ollama的向量模型和聊天模型都为空就返回空list
                return []
            else:
                # 使用聊天的模型进行向量数据的生成
                model = OLLAMA_DATA.get("model")
            # 去掉文本中的换行符，保证输入格式规范
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input=[text], model=model).data[0].embedding
