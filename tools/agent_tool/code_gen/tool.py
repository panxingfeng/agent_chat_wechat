# 保持原有的工具定义和类不变
import logging
from typing import ClassVar
import requests
from langchain.agents import tool
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class CodeGenAPIWrapper(BaseModel):
    base_url: ClassVar[str] = "http://localhost:11434/api/chat"
    content_role: ClassVar[str] = (
        "你是一个精通编程的代码助手，"
        "能够根据用户的需求编写代码。"
    )
    model: str = "qwen2.5-coder"

    def run(self, query: str, model_name: str) -> str:
        logging.info(f"使用模型 {model_name} 处理用户请求: {query}")
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": self.content_role + query}],
            "stream": False,
        }
        response = requests.post(self.base_url, json=data)
        response.raise_for_status()

        try:
            result = response.json()
            return result.get("message", {}).get("content", "无法生成代码，请检查输入。")
        except requests.exceptions.JSONDecodeError as e:
            return f"解析 JSON 时出错: {e}"

    def generate_code(self, query: str) -> str:
        try:
            result = self.run(query, self.model)
            if "无法生成代码" not in result:
                return result
        except Exception as e:
            logging.error(f"生成代码时出错: {e}")
        return "代码生成失败，请稍后再试。"

# 实例化 CodeGenAPIWrapper，用于代码生成
code_generator = CodeGenAPIWrapper()

@tool
def code_gen(query: str) -> str:
    """代码生成工具：根据用户描述生成相应的代码实现。"""
    return code_generator.generate_code(query)

# 添加 register_tool 函数，用于显式返回工具信息
def register_tool():
    return {
        "agent_tool": code_gen,
        "description": code_gen.__doc__
    }
