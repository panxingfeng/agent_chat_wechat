from config.config import OLLAMA_DATA
from config.templates.data.bot import CODE_BOT_PROMPT_DATA
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient


def code_gen(query: str, code_type: str) -> str:
    """代码生成工具：根据用户描述生成相应的代码实现。"""
    client = OllamaClient()
    print("使用代码生成工具")
    prompt = CODE_BOT_PROMPT_DATA.get("description").format(code_type=code_type)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": query}
    ]

    response = client.invoke(messages, model=OLLAMA_DATA.get("code_model"))
    return response
