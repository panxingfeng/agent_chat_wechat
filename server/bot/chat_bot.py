import asyncio
import json
import logging

import pynvml
import redis
import os
from datetime import datetime
from langchain_openai import ChatOpenAI

from config.config import CHATGPT_DATA, REDIS_DATA, OLLAMA_DATA, MOONSHOT_DATA, BAICHUAN_DATA
from config.templates.data.bot import MAX_HISTORY_SIZE, MAX_HISTORY_LENGTH, BOT_DATA, CHATBOT_PROMPT_DATA
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient
from server.client.online.BaiChuanClient import BaiChuanClient
from server.client.online.moonshotClient import MoonshotClient

# 配置日志记录系统
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# 获取当前文件所在的路径
base_dir = os.path.dirname(os.path.abspath(__file__))

# 配置Redis连接池
redis_pool = redis.ConnectionPool(host=REDIS_DATA.get("host"), port=REDIS_DATA.get("port"), db=REDIS_DATA.get("db"))
redis_client = redis.StrictRedis(connection_pool=redis_pool)

# 获取当前系统时间
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ChatBot:
    def __init__(self, user_name, user_id):
        """初始化ChatBot类，设置用户信息和查询，加载OpenAI模型"""
        self.user_id = user_id  # 将用户ID作为会话ID
        self.user_name = user_name  # 用户名称
        self.redis_key_prefix = "chat_history:"  # Redis存储键的前缀
        self.history = []  # 用于存储会话历史记录的列表
        self.model = self.get_model_client()

    def get_model_client(self):
        """根据配置文件选择返回的模型"""
        if OLLAMA_DATA.get("use"):
            logging.info(f"使用Ollama模型生成回复: {OLLAMA_DATA.get('model')}")
            return OllamaClient()  # 使用Ollama模型
        elif MOONSHOT_DATA.get("use") and MOONSHOT_DATA.get("key") is not None:
            logging.info(f"使用kimi模型生成回复: {MOONSHOT_DATA.get('model')}")
            return MoonshotClient()  # 使用Moonshot模型
        elif BAICHUAN_DATA.get("use") and BAICHUAN_DATA.get("key") is not None:
            logging.info(f"使用百川模型生成回复: {BAICHUAN_DATA.get('model')}")
            return BaiChuanClient()  # 使用百川模型
        elif CHATGPT_DATA.get("use") and CHATGPT_DATA.get("key") is not None:
            logging.info(f"使用OpenAI模型生成回复: {CHATGPT_DATA.get('model')}")
            return ChatOpenAI(
                api_key=CHATGPT_DATA.get("key"),
                base_url=CHATGPT_DATA.get("url"),
                model=CHATGPT_DATA.get("model")
            )
        return "所有模型出错，key为空或者没有设置‘use’为True"  # 返回错误信息

    def format_history(self):
        """从Redis获取并格式化历史记录"""
        history = self.get_history_from_redis(self.user_id)  # 从Redis获取历史记录
        if not history:
            logging.info("没有从Redis中获取到历史记录")
            return ""

        formatted_history = []
        for entry in history:
            human_text = entry.get('Human', '')
            formatted_history.append(f"Human: {human_text}\n")  # 格式化用户消息

        return "\n".join(formatted_history)  # 返回格式化后的历史记录

    def get_history_from_redis(self, user_id):
        """从Redis获取历史记录"""
        key = f"{self.redis_key_prefix}{user_id}"  # 生成Redis的键名
        try:
            history = redis_client.get(key)  # 获取历史记录
            if history:
                return json.loads(history)  # 如果存在历史记录，解析为JSON格式
        except redis.RedisError as e:
            logging.error(f"从Redis获取历史记录时出错: {e}")
        return []  # 如果出现错误或没有历史记录，返回空列表

    def save_history_to_redis(self, user_id, history):
        """将历史记录保存到Redis"""
        key = f"{self.redis_key_prefix}{user_id}"  # 生成Redis的键名
        try:
            redis_client.set(key, json.dumps(history))  # 将历史记录保存为JSON格式
        except redis.RedisError as e:
            logging.error(f"保存历史记录到Redis时出错: {e}")

    def manage_history(self):
        """管理历史记录：删除最早的记录或截断字符长度"""
        self.history = self.get_history_from_redis(self.user_id)  # 获取历史记录

        # 如果历史记录数量超过最大值，删除最早的记录
        while len(self.history) > MAX_HISTORY_SIZE:
            self.history.pop(0)

        history_str = json.dumps(self.history)  # 将历史记录转换为JSON字符串
        # 如果历史记录的总字符长度超过最大限制，逐步删除最早的记录
        while len(history_str) > MAX_HISTORY_LENGTH:
            if self.history:
                self.history.pop(0)
                history_str = json.dumps(self.history)
            else:
                break

    def generate_response(self, query):
        """生成AI回复"""
        try:
            # 如果使用的是百川模型，不支持设置系统提示词
            if BAICHUAN_DATA.get("use") and BAICHUAN_DATA.get("key") is not None:
                messages = [
                    {"role": "user", "content": query}  # 只包含用户的消息
                ]
            else:
                # 设置模型的提示词信息，包括历史记录、欢迎信息等
                instructions = CHATBOT_PROMPT_DATA.get("description").format(
                    name=BOT_DATA["agent"].get("name"),
                    capabilities=BOT_DATA["agent"].get("capabilities"),
                    welcome_message=BOT_DATA["agent"].get("default_responses").get("welcome_message"),
                    unknown_command=BOT_DATA["agent"].get("default_responses").get("unknown_command"),
                    language_support=BOT_DATA["agent"].get("language_support"),
                    history=self.format_history(),
                    query=query,
                )
                messages = [
                    {"role": "system", "content": instructions},  # 系统提示词
                    {"role": "user", "content": query}  # 用户的提问
                ]
            response = self.model.invoke(messages)  # 调用模型生成回复
            if response:
                logging.info(f"成功生成回复")
                return response.content  # 返回生成的回复内容
        except Exception as e:
            logging.warning(f"模型生成回复失败: {e}")
            return "模型生成回复失败，请稍后再试。"  # 处理异常并返回错误信息

    async def run(self, user_name, query, user_id, image_path, file_path):
        """主运行逻辑，管理历史记录、生成回复，并保存会话记录"""
        logging.info(f"接收到用户id为：{user_id}，用户名为{user_name}的消息")
        self.manage_history()  # 管理历史记录

        # 将用户输入加入历史记录
        self.history.append({
            "Human": query,
        })

        # 生成AI回复
        response = self.generate_response(query)

        # # 可以选择将生成的回复加入历史记录
        # self.history.append({
        #     "AI": response,
        # })

        # 保存更新后的历史记录到Redis
        self.save_history_to_redis(self.user_id, self.history)

        return response  # 返回生成的回复

if __name__ == "__main__":
    query = "你好啊"
    user_id = "0101"
    user_name = "pan"
    bot = ChatBot(user_id=user_id, user_name=user_name)

    # 运行异步函数
    response = asyncio.run(bot.run(user_id=user_id, query=query, user_name=user_name, file_path=None, image_path=None))

    print(response)
