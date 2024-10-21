from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from config.templates.data.bot import CODE_BOT_PROMPT_DATA
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient


def code_gen(query: str, code_type: str) -> str:
    """代码生成工具：根据用户描述生成相应的代码实现。"""
    client = OllamaClient()
    prompt = CODE_BOT_PROMPT_DATA.get("description").format(code_type=code_type)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": query}
    ]

    response = client.invoke(messages)
    return response

def search_tool(query: str) -> str:
    """联网搜索工具"""
    # 初始化 DuckDuckGoSearchAPIWrapper
    wrapper = DuckDuckGoSearchAPIWrapper(region="de-de", time="d", max_results=2)

    # 创建 DuckDuckGoSearchResults 实例
    search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")

    # 执行搜索
    result = search.invoke(query)
    return result
