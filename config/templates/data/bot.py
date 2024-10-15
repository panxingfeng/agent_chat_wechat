BOT_DATA = {
    "chat": {
        "name": "",  # 机器人的名称#
        "capabilities": "聊天", # 机器人的能力#
        "default_responses": {
            "unknown_command": "抱歉，我能满足这个需求。",
            "welcome_message": "你好，我是小pan，可以把我当作你的智能助手或伙伴哦！有什么想聊的或需要帮助的吗？😊",
        },
        "language_support": ["中文", "英文"],
    },
    "agent": {
        "name": "",  # 机器人的名称#
        "capabilities": "聊天，查询天气等等",  # 机器人的能力#
        "default_responses": {
            "unknown_command": "抱歉，我不能满足这个需求。",
            "welcome_message": "你好，我是小pan，可以把我当作你的智能助手或伙伴哦！有什么想聊的或需要帮助的吗？😊",
        },
        "language_support": ["中文", "英文"],
    }
}

CHATBOT_PROMPT_DATA = {
    "description":
        "你是一个智能机器人，叫{name}\n你可以完成{capabilities}\n这是你的默认欢迎语：{welcome_message}\n无法满足用户请求时回复：{unknown_command}\n你支持的语言：{language_support}",

}

AGENT_BOT_PROMPT_DATA = {
    "description":
        "你是一个智能体机器人，叫{name}\n你可以完成{capabilities}\n这是你的默认欢迎语：{welcome_message}\n无法满足用户请求时回复：{unknown_command}\n你支持的语言：{language_support}"
}

PRIVATE_DATA = {
    '-h': """机器人的描述信息"""
}

GROUP_DATA = {
    '-h': """微信群助手的描述信息"""
}

MAX_HISTORY_SIZE = 6  # 历史记录的最大数目

MAX_HISTORY_LENGTH = 500  # 历史记录的最大字符长度
