# AgentChatBot

<div align="center">

![Python](https://img.shields.io/badge/python-3.10-blue)
![Framework](https://img.shields.io/badge/framework-langchain-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

基于 langchain/Ollama 的智能对话机器人，支持微信与飞书部署
</div>

## 📚 目录

- [项目概览](#-项目概览)
- [核心功能](#-核心功能)
- [最新更新](#-最新更新)
- [快速开始](#-快速开始)
- [配置说明](#-配置说明)
- [工具开发](#-工具开发)
- [开发计划](#-开发计划)
- [模型支持](#-模型支持)
- [相关项目](#-相关项目)

## 🌟 项目概览

AgentChatBot 是一个基于 langchain/Ollama 的智能体框架，支持：
- 🤖 私人微信部署 (通过 VChat)
- 💼 飞书机器人集成
- 🎨 React UI 界面
- 🛠 自定义工具扩展

## 🚀 核心功能

### 代码生成
- 基于本地 Ollama 部署
- 支持多种编程语言
- 智能代码补全

### 多平台支持
- ✅ 微信接入
- ✅ 飞书部署
- ✅ React UI 界面
- 🔧 更多平台持续集成中...

## 📢 最新更新

### 2024-10-16
- 🆕 新增 Swarm Agent 框架支持
  - 实现智能客服示例（水果店场景）
  - 支持 Ollama/GPT 双模式切换
  ```bash
  # Ollama模式
  OLLAMA_DATA{'use': True}  # config/config.py
  
  # GPT模式
  CHATGPT_DATA{'use': True}  # config/config.py
  ```

## 🚀 快速开始

### 环境依赖

<details>
<summary>点击展开详细安装步骤</summary>

1. **基础环境**
   - [Redis 安装教程](https://blog.csdn.net/weixin_43883917/article/details/114632709)
   - [MySQL 安装教程](https://blog.csdn.net/weixin_41330897/article/details/142899070)
   - [Ollama 安装教程](https://blog.csdn.net/qq_40999403/article/details/139320266)
   - [Anaconda 安装教程](https://blog.csdn.net/weixin_45525272/article/details/129265214)

2. **项目安装**
```bash
# 克隆项目
git clone https://github.com/panxingfeng/agent_chat_wechat.git
cd agent_chat_wechat

# 创建环境
conda create --name agent_wechat python=3.10
conda activate agent_wechat

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install aiohttp pytz vchat langchain_openai transformers -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install mysql-connector-python langchain pillow aiofiles -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install git+https://github.com/openai/swarm.git

# 启动项目
python main.py
```
</details>

### 🤖 启动智能体
在聊天框中输入 `#智能体` 即可激活。

## ⚙️ 配置说明

<details>
<summary>配置文件示例 (config/config.py)</summary>

```python
CHATGPT_DATA = {
    'use': False,
    'model': 'gpt-4o-mini',
    'key': '',
    'url': 'https://api.openai.com/v1',
    'temperature': 0.7,
}

OLLAMA_DATA = {
    'use': True,
    'model': 'qwen2.5',
    'key': 'EMPTY',
    'api_url': 'http://localhost:11434/v1/'
}

# 更多配置选项...
```
</details>

## 🛠 工具开发

### GPT Agent 工具模板
<details>
<summary>展开查看代码模板</summary>

```python
class CodeGenAPIWrapper(BaseModel):
    # 工具实现代码...
```
</details>

### Swarm Agent 工具模板
<details>
<summary>展开查看代码模板</summary>

```python
def code_gen(query: str, code_type: str) -> str:
    # 工具实现代码...
```
</details>

## 📅 开发计划

1. ✅ RAG 快速检索客服助手
2. ✅ React 框架支持
   - 流式输出
   - 文生图/图生图 (SD-webui API)
   - 知识库功能
   - 语音功能
   - 智能体创建
3. 🚧 GraphRAG v2
4. 🚧 语音集成 (F5-TTS/GPT-SoVITS)
5. 🚧 Agent 工作流框架

## 🤖 模型支持

- ChatGPT 系列
- Ollama 全系列
- 国内主流模型（百川、MoonShot等）

<div align="center">
<img src="./images/img4.png" width="400" />
<img src="./images/img5.png" width="400" />
</div>

## 🔗 相关项目

- [VChat 框架](https://github.com/z2z63/VChat)
- [SD-on-phone](https://github.com/panxingfeng/Stable-Diddusion-on-phone)
- [AIChat_UI](https://github.com/panxingfeng/AIChat_UI)

---

<div align="center">
⭐️ 如果这个项目对你有帮助，欢迎 Star 支持！⭐️
</div>
