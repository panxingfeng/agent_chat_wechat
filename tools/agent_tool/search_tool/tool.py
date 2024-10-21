import logging
from langchain.agents import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class SearchAPIWrapper(BaseModel):
    def run(self, query: str) -> str:
        # 初始化 DuckDuckGoSearchAPIWrapper
        wrapper = DuckDuckGoSearchAPIWrapper(region="de-de", time="d", max_results=2)

        # 创建 DuckDuckGoSearchResults 实例
        search = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")

        # 执行搜索
        response = search.invoke(query)

        return response

    def generate_result(self, query: str) -> str:
        try:
            result = self.run(query)
            if result is not None:
                return result
        except Exception as e:
            logging.error(f"搜索时出错: {e}")
        return "使用搜索工具失败"


search = SearchAPIWrapper()


@tool
def search_tool(query: str) -> str:
    """联网搜索工具"""
    return search.generate_result(query)


# 返回工具信息
def register_tool():
    tool_func = search_tool  # 工具函数
    tool_func.__name__ = "search_tool"
    return {
        "name": "search_tool",
        "agent_tool": tool_func,
        "description": "联网搜索工具"
    }
