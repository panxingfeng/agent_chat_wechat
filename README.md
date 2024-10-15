# ChatBot 项目


## 目录

- [项目简介](#项目简介)
- [功能](#功能)
- [安装与配置](#安装与配置)
- [使用说明](#使用说明)
- [许可证](#许可证)
- [工具代码模板](#工具代码模板)
- [如何添加工具到智能体](#如何添加工具到智能体)
- [预计更新内容](#预计更新内容)
- [VChat框架](#VChat框架)

## 项目简介

本项目是基于langchain的agent实现多功能的智能体机器人，通过vchat部署到私人微信中。

可以自行设计与实现各种工具，供agent调用

支持模型：ChatGPT模型，ollama客户端的所有模型

项目代码中增加了

```bash
    qwen 0.5b/1.5b
    baichuan
    mini
```


## 功能

- **代码生成**: 使用本地部署的ollama客户端运行code类的模型进行代码的生成
- ......


## 安装与配置

### 依赖安装

1. **Redis 安装**：[参考教程](https://blog.csdn.net/weixin_43883917/article/details/114632709)  
2. **MySQL 安装**：[参考教程](https://blog.csdn.net/weixin_41330897/article/details/142899070)  

3. 克隆仓库：
    ```bash
    git clone https://github.com/panxingfeng/agent_chat_wechat.git
    cd <项目目录>
    ```

4. 创建并激活虚拟环境：
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # 在 Windows 上使用 .venv\Scripts\activate
    ```

5. 安装依赖(使用清华源)：
    ```bash
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    ```

6. 运行：
    ```bash
    python main.py
    ```
7. 说明：开启agent智能体机器人，需要在聊天框中输入  #智能体  即可。
### 配置文件

项目的配置文件 `config/config.py` 包含了应用所需的配置信息。请根据实际情况修改该文件中的配置项


### 使用说明
运行 python main.py，然后按照提示进行操作。

### 许可证
本项目使用 MIT 许可证 开源。

### 工具代码模板
在智能体中添加工具时，您可以使用以下代码模板：
```bash
class CodeGenAPIWrapper(BaseModel):
    base_url: ClassVar[str] = "http://localhost:11434/api/chat"
    content_role: ClassVar[str] = (
        "你是一个精通编程的代码助手，"
        "能够根据用户的需求编写代码。"
    )
    model: str = "qwen2.5-coder" #可以使用其他的本地模型，自行修改

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

code_generator = CodeGenAPIWrapper()

@tool
def code_gen(query: str) -> str:
    """代码生成工具：根据用户描述生成相应的代码实现。"""
    return code_generator.generate_code(query)

# 返回工具信息
def register_tool():
    return {
        "agent_tool": code_gen,
        "description": "代码生成工具"
    }


   ```

### 如何添加工具到智能体
1.根据示例工具代码进行编写工具代码

2.在tools/agent_tool目录下，增加一个工具的文件夹（例如：code_gen）

3.把工具代码保存为tool.py即可


### 预计更新内容

1.基于RAG快速检索，完成自定义的客服助手(需要检索资料的文档放置serve/rag/file中即可)，提示词在config/templates/data/bot中修改(近期上传，还在编写中)

2.使用本地Ollama实现agent-bot处理(近期上传)

3.基于最新消息，持续更新工具内容(近期上传)


### VChat框架
VChat框架地址：https://github.com/z2z63/VChat
