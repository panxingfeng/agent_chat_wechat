# ChatBot 项目

这是一个基于 Python 的聊天机器人项目，使用了 FastAPI、LangChain、OpenAI、Redis 和其他工具来实现多功能的聊天体验。项目包括音乐搜索、二维码生成、历史事件查询等功能。

## 目录

- [项目简介](#项目简介)
- [功能](#功能)
- [安装与配置](#安装与配置)
- [使用说明](#使用说明)
- [贡献](#贡献)
- [许可证](#许可证)

## 项目简介

本项目是一个多功能的聊天机器人应用，通过集成多个工具和服务，提供丰富的用户交互体验。主要功能包括音乐搜索、60秒早报、历史事件查询和二维码生成等。

## 功能

- **音乐搜索**: 通过音乐名称搜索相关的音乐资源，提供歌曲名称、作者、播放链接和封面图片链接。
- **60秒早报**: 获取并返回60秒早报的内容。
- **历史上的今天**: 查询历史上的今天发生的事件，并返回标题、URL和日期。
- **二维码生成**: 根据输入的文本生成二维码，并返回二维码图片的URL。
- **视频下载**: 从指定的URL获取视频信息并下载到本地文件夹。

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
