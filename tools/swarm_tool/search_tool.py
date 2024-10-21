from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


def search_tool(query: str) -> str:
    # 初始化 DuckDuckGoSearchAPIWrapper
    wrapper = DuckDuckGoSearchAPIWrapper(region="de-de", time="d", max_results=2)

    # 创建 DuckDuckGoSearchResults 实例
    search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")

    # 执行搜索
    result = search.invoke(query)
    return result
