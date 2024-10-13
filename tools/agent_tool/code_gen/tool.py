import logging
from typing import ClassVar
import requests
from pydantic import BaseModel
from langchain.agents import StructuredTool, tool

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class CodeGen(BaseModel):
    """代码生成工具类，使用 HTTP 请求生成代码。"""
    base_url: ClassVar[str] = "http://localhost:11434/api/chat"
    content_role: str = "你是一个精通编程的代码助手。你可以使用多种编程语言，并能够根据用户的需求编写代码。这是客户的需求："

    def run(self, query: str) -> str:
        """向模型发送代码生成请求，并返回结果。"""
        model_name: str = "qwen2.5"
        logging.info(f"使用模型 {model_name} 接收到用户的问题: {query} ----> 代码生成")
        data = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": self.content_role + query
                }
            ],
            "stream": False
        }
        response = requests.post(self.base_url, json=data)
        response.raise_for_status()

        try:
            result = response.json()
            content = result.get("message", {}).get("content", "无法生成代码，请检查输入。")
            return content
        except requests.exceptions.JSONDecodeError as e:
            return f"解析 JSON 时出错: {e}"

    def describe(self) -> str:
        """返回工具的描述信息。"""
        model_name: str = "qwen2.5"
        return f"代码生成工具 (使用模型: {model_name})"


# 将工具注册为 StructuredTool
code_gen_tool = StructuredTool.from_function(
    name="code_gen",
    description="只有需要生成任何的代码才使用这个工具",
    func=CodeGen().run,  # 确保传入的是可调用对象
)

def register_tool() -> dict:
    """
    注册工具，并返回工具的引用和描述。
    """
    skit_api = CodeGen()  # 实例化工具类
    return {
        "agent_tool": code_gen_tool,
        "description": skit_api.describe(),
    }

