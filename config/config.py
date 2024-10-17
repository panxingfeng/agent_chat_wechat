#########################################  离线/本地的大模型信息  #########################################

CHATGPT_DATA = {
    'use': False,
    'model': 'gpt-4o-mini',  # 模型名称，GPT 模型的具体版本
    'key': '', # 你的 OpenAI API 密钥
    'url': 'https://api.openai.com/v1',  # OpenAI API 的地址
    'temperature': 0.7,  # 生成内容的多样性程度，0-1 范围内
}

OLLAMA_DATA = {
    'use': False,  
    'model': 'qwen2.5',  # ollama运行的模型名称
    'code_model': 'qwen2.5',
    'key': 'EMPTY',
    'url': 'http://localhost:11434/api/chat',  # 本地 Ollama 服务地址
    'api_url': "http://localhost:11434/v1/"
}

MOONSHOT_DATA = {
    'use': False,
    'key': "",
    'url': "https://api.moonshot.cn/v1",
    'model': "moonshot-v1-8k",
    "prompt": ""
}

BAICHUAN_DATA = {
    'use': False,
    'key': "",
    'url': "https://api.baichuan-ai.com/v1/",
    'model': "Baichuan2-Turbo"
    # 百川模型不支持自定义提示词内容#
}

#########################################  本地数据库信息  #########################################

# 本地mysql数据库信息
DB_DATA = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',  # 数据库用户
    'password': '1234',  # 数据库密码
    'database': 'agent'  # 数据库名称
}

# redis信息
REDIS_DATA = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

#########################################  wechat信息  #########################################

# 微信中的文件保存到本地的地址信息#
DOWNLOAD_ADDRESS = {
    'file': 'D:\\xxxx\\file',
    'vidio': 'D:\\xxxx\\vidio',
    'audio': 'D:\\xxxx\\audio',
    'image': 'D:\\xxxx\\image'
}

#登录微信的基本信息
LOGIN_WECHAT_DATA = {
    "name": "xxx",  # 微信用户名（对方@xxx的xxx）
    "manner_name": ""  # 群管理人员信息
}
