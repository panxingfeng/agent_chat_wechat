CHATGPT_DATA = {
    'model': 'gpt-4o-mini',  # 模型名称，GPT 模型的具体版本
    'key': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',  # 你的 OpenAI API 密钥
    'url': 'https://api.openai.com/v1',  # OpenAI API 的地址
    'temperature': 0.7  # 生成内容的多样性程度，0-1 范围内
}

OLLAMA_DATA = {
    'model_name': 'gpt-4o-mini',  # 本地模型名称
    'key': 'EMPTY',  # 如果没有密钥需求，可以留空
    'ollama_url': 'http://localhost:11434/api/chat'  # 本地 Ollama 服务地址
}

DB_DATA = {
    'host': 'localhost',  # 数据库地址
    'user': 'root',  # 数据库用户
    'password': '1234',  # 数据库密码
    'database': 'agent'  # 数据库名称
}

DOWNLOAD_ADDRESS = {
    'file': 'D:\\output\\wechatMessage\\file',
    'vidio': 'D:\\output\\wechatMessage\\vidio',
    'audio': 'D:\\output\\wechatMessage\\audio',
    'image': 'D:\\output\\wechatMessage\\image'
}

LOGIN_WECHAT_DATA = {
    "name": "panllq",  # 微信用户名
    "manner_name": "pan"  # 登录后展示的名称
}

PRIVATE_DATA = {
    '-h': """机器人的描述信息"""
}

GROUP_DATA = {
    '-h': """微信群助手的描述信息"""
}
