# ChatBot 项目


## 目录

- [项目简介](#项目简介)
- [功能](#功能)
- [安装与配置](#安装与配置)
- [使用说明](#使用说明)
- [贡献](#贡献)
- [许可证](#许可证)
- [工具代码模板](#工具代码模板)
- [如何添加工具到智能体](#如何添加工具到智能体)

## 项目简介

本项目是一个多功能的聊天机器人应用，通过集成多个工具和服务，提供丰富的用户交互体验。主要功能包括音乐搜索、60秒早报、历史事件查询和二维码生成等。

这是属于简易代码版本，可以自行设计与实现各种工具，供agent调用，完整代码不做上传

完整代码功能包含
```bash
实时搜索工具： 搜索实时信息，支持综合查询和短剧搜索。
代码生成工具： 根据需求生成代码，支持多种编程语言。
代码解析工具： 对输入的代码进行功能、结构、逻辑分析。
图像识别工具： 提供图像识别功能，根据图像文件和问题进行识别。
绘画生成工具： 根据输入的文字描述生成绘画。
语音生成工具： 将文本转换为语音，支持多种语音生成。
向量数据库操作工具： 将文档或文本消息保存到用户特定的向量数据库中，并支持查询和搜索。
消息定时工具： 设置定时消息提醒，并将任务保存到数据库中。
音乐搜索工具： 搜索音乐资源，返回播放链接和封面图片。
视频下载工具： 从指定 URL 获取视频信息并下载视频到本地。
二维码生成工具： 根据输入文本生成二维码并返回其 URL。
定时任务启动：设定一个时间，启动设置的任务。
......
```

## 功能

- **音乐搜索**: 通过音乐名称搜索相关的音乐资源，提供歌曲名称、作者、播放链接和封面图片链接。
- **60秒早报**: 获取并返回60秒早报的内容。
- **历史上的今天**: 查询历史上的今天发生的事件，并返回标题、URL和日期。
- **二维码生成**: 根据输入的文本生成二维码，并返回二维码图片的URL。

## 安装与配置

### 依赖安装

1. 克隆仓库：
    ```bash
    git clone https://github.com/panxingfeng/agent_chat_wechat.git
    cd <项目目录>
    ```

2. 创建并激活虚拟环境：
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # 在 Windows 上使用 .venv\Scripts\activate
    ```

3. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

4. 运行：
    ```bash
    python main.py
    ```

### 配置文件

项目的配置文件 `config/config.json` 包含了应用所需的配置信息。请根据实际情况修改该文件中的配置项：

```json
{
    "redis_host": "localhost",
    "redis_port": 6379,
    "redis_db": 0,
    "openai_api_key": "your_openai_api_key",
    "openai_api_base": "https://api.openai.com/v1",
    "openai_model_name": "gpt-3.5-turbo",
    "download_vido_path": "path_to_download_folder"
}
```

### 使用说明
运行 python main.py，然后按照提示进行操作。

### 贡献
欢迎对项目进行贡献。如果您有任何建议或发现问题，请提交 issue 或 pull request。

### 许可证
本项目使用 MIT 许可证 开源。

### 工具代码模板
在智能体中添加工具时，您可以使用以下代码模板：
```bash
@tool
def tool_function_name(param1: str, param2: str) -> str:
    """工具功能描述"""

    base_url = 'https://example.com/api/endpoint'  # 替换为实际的API URL
    params = {
        "param1": param1,
        "param2": param2,
        # 添加其他参数
    }

    try:
        response = requests.get(base_url, params=params, proxies={"http": None, "https": None})
        response.raise_for_status()  # 检查请求是否成功

        # 处理响应数据
        data = response.json()
        result = data.get('result', '未找到结果')

        return result

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
        return ""
    except requests.exceptions.RequestException as err:
        print(f"请求错误发生: {err}")
        return ""
   ```

### 如何添加工具到智能体
1. 编写工具函数: 使用上面的代码模板编写工具函数。确保您的函数使用 @tool 装饰器，并处理可能出现的异常。

2. 更新智能体配置: 在 chatBot_agent.py 文件中，找到工具列表部分。例如：
```bash
# 工具列表
tools = [
    tool_function_name,
    # 其他工具
]
```
3. 保存并测试: 保存对 chatBot_agent.py 的更改，然后运行应用程序以确保新工具正常工作。###