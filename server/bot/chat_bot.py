import json
import logging
import redis
import os
from datetime import datetime
from langchain_openai import ChatOpenAI

from config.config import CHATGPT_DATA, REDIS_DATA, OLLAMA_DATA
from server.client.ollama_client import OllamaClient

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


class Chat_Bot_Chat:
    MAX_HISTORY_SIZE = 6  # 历史记录的最大条目数
    MAX_HISTORY_LENGTH = 500  # 历史记录的最大字符长度

    def __init__(self, user_name, user_id):
        """初始化ChatBot类，设置用户信息和查询，加载OpenAI模型"""
        self.user_id = user_id  # 将用户ID作为会话ID
        self.user_name = user_name  # 用户名称
        self.redis_key_prefix = "chat_history:"  # Redis存储键的前缀
        self.history = []  # 用于存储会话历史记录的列表

        # 动态加载OpenAI模型
        self.model = self.get_model_client()

    def get_model_client(self):
        """根据配置文件选择返回的模型"""
        if OLLAMA_DATA.get("use"):
            logging.info(f"使用Ollama模型生成回复: {OLLAMA_DATA.get('model')}")
            return OllamaClient(
                model=OLLAMA_DATA.get("model"),
                url=OLLAMA_DATA.get("url")
            )
        else:
            logging.info(f"使用OpenAI模型生成回复: {CHATGPT_DATA.get('model')}")
            return ChatOpenAI(
                api_key=CHATGPT_DATA.get("key"),
                base_url=CHATGPT_DATA.get("url"),
                model=CHATGPT_DATA.get("model")
            )

    def manage_history(self):
        """管理会话历史记录，从Redis加载历史记录，并限制记录的大小和字符长度"""
        key = f"{self.redis_key_prefix}{self.user_id}"
        try:
            # 从Redis获取历史记录
            history = redis_client.get(key)
            if history:
                self.history = json.loads(history)
        except redis.RedisError as e:
            logging.error(f"从Redis获取历史记录时出错: {e}")

        # 限制历史记录的条目数
        while len(self.history) > self.MAX_HISTORY_SIZE:
            self.history.pop(0)

        # 限制历史记录的总字符长度
        history_str = json.dumps(self.history)
        while len(history_str) > self.MAX_HISTORY_LENGTH:
            if self.history:
                self.history.pop(0)
                history_str = json.dumps(self.history)
            else:
                break

    def save_history_to_redis(self):
        """将更新后的历史记录保存到Redis"""
        key = f"{self.redis_key_prefix}{self.user_id}"
        try:
            redis_client.set(key, json.dumps(self.history))
        except redis.RedisError as e:
            logging.error(f"保存历史记录到Redis时出错: {e}")

    def generate_response(self, query):
        """生成AI回复"""
        try:
            # 调用invoke时，需要传入适合的消息结构
            messages = [
                {"role": "system", "content": "你是一个智能助手"},
                {"role": "user", "content": query}
            ]
            response = self.model.invoke(messages)
            if response:
                logging.info(f"成功生成回复")
                return response.content  # 确保返回内容
        except Exception as e:
            logging.warning(f"模型生成回复失败: {e}")
            return "模型生成回复失败，请稍后再试。"

    async def run(self, user_name, query, user_id):
        """主运行逻辑，管理历史记录、生成回复，并保存会话记录"""
        logging.info(f"接收到用户id为：{user_id}，用户名为{user_name}的消息")
        self.manage_history()

        # 将用户输入加入历史记录
        self.history.append({
            "Human": query,
        })

        # 生成AI回复
        response = self.generate_response(query)

        # # 将生成的回复加入历史记录
        # self.history.append({
        #     "AI": response,
        # })
        # 可以做保存也可以不做保存

        # 保存更新后的历史记录到Redis
        self.save_history_to_redis()

        return response
