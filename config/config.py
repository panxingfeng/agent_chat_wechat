CHATGPT_DATA = {
    'model': 'gpt-4o-mini',  # 模型名称，GPT 模型的具体版本
    'key': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',  # 你的 OpenAI API 密钥
    'url': 'https://api.openai.com/v1',  # OpenAI API 的地址
    'temperature': 0.7  # 生成内容的多样性程度，0-1 范围内
}

OLLAMA_DATA = {
    'use': True, #是否开启使用ollama客户端，默认为True
    'model_name': 'qwen2.5',  # ollama运行的模型名称
    'key': 'EMPTY', 
    'ollama_url': 'http://localhost:11434/api/chat'  # 本地 Ollama 服务地址
}

DB_DATA = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',  # 数据库用户
    'password': '1234',  # 数据库密码
    'database': 'agent'  # 数据库名称
}

#微信中需要保存的文件地址#
DOWNLOAD_ADDRESS = {
    'file': 'D:\\agent\\wechat\\file',
    'vidio': 'D:\\agent\\wechat\\vidio',
    'audio': 'D:\\agent\\wechat\\audio',
    'image': 'D:\\agent\\wechat\\image'
}

LOGIN_WECHAT_DATA = {
    "name": "xxx",  # 微信用户名（对方@xxx的xxx）
    "manner_name": ""  # 群管理人员信息
}

PRIVATE_DATA = {
    '-h': """机器人的描述信息"""
}

GROUP_DATA = {
    '-h': """微信群助手的描述信息"""
}

REDIS_DATA = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}
