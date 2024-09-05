import traceback
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tools import *
import logging
from datetime import datetime
from pydub import AudioSegment
import json
import redis
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from tools.tools import *

# 设置日志记录
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# 获取当前脚本所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))
# 配置文件路径
config_path = os.path.join(base_dir, "../config/config.json")
# 读取配置文件
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

# 设置 OpenAI API 的密钥和基础 URL
os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
os.environ["OPENAI_API_BASE"] = config["openai_api_base"]

# Redis 连接池
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.StrictRedis(connection_pool=redis_pool)

# 存储会话中的图像路径
user_image_map = {}

# 存储会话中的文件路径
user_file_map = {}

# 执行任务的线程池
executor = ThreadPoolExecutor(max_workers=20)

# 当前时间
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Chat_Bot_Agent:
    MAX_HISTORY_SIZE = 6
    MAX_HISTORY_LENGTH = 500

    def __init__(self, user_name, user_id):
        # 初始化两个不同的 OpenAI 聊天模型
        self.chatModel_4o_mini = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            streaming=True
        )
        self.chatModel_3_5 = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            streaming=True
        )
        # 用户 ID 和用户名
        self.user_id = user_id  # 使用用户 ID 作为 session_id
        self.user_name = user_name
        self.redis_key_prefix = "chat_history:"  # Redis 中的历史记录键前缀
        self.history = []  # 历史记录列表
        self.saved_files = {}  # 保存文件路径
        # 系统提示模板
        self.SYSTEMPL = """
        你是一个智能化的全能机器人，具备广泛的知识和实时数据处理能力。

        ### 个人设定:

        ### 历史记录:
        {history}

        ### 当前时间:
        {current_time}

        ### 用户id:
        {user_id}

        ### 用户名:
        {user_name}

        ### 工具说明：


        ### 常用短语:


        ### 处理问题的过程:

        """
        # 创建聊天模板
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEMPL.format(current_time=current_time, history=self.format_history(), user_name=self.user_name, user_id=self.user_id),
                ),
                (
                    "user",
                    "{input}"
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )

        # 工具列表
        tools = [search_music,  # 音乐搜索工具
                 fetch_60s_report,  # 60s早报工具
                 fetch_history_today,
                 generate_qr_code,
                 ]

        # 创建两个不同的 OpenAI 工具代理
        agent = create_openai_tools_agent(
            self.chatModel_4o_mini,
            tools=tools,
            prompt=self.prompt
        )

        agent_substitute = create_openai_tools_agent(
            self.chatModel_3_5,
            tools=tools,
            prompt=self.prompt
        )

        # 创建 AgentExecutor 对象
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True
        )
        self.agent_executor_substitute = AgentExecutor(
            agent=agent_substitute,
            tools=tools,
            verbose=True
        )

    def update(self, user_id, query, user_name):
        # 更新用户信息
        self.user_id = user_id
        self.query = query
        self.user_name = user_name

    def format_history(self):
        """从Redis获取并格式化历史记录"""
        history = self.get_history_from_redis(self.user_id)
        if not history:
            logging.info("没有从Redis中获取到历史记录")
            return ""

        formatted_history = []
        for entry in history:
            human_text = entry.get('Human', '')

            formatted_history.append(f"Human: {human_text}\n")

        return "\n".join(formatted_history)

    def get_history_from_redis(self, user_id):
        """从Redis获取历史记录"""
        key = f"{self.redis_key_prefix}{user_id}"
        try:
            history = redis_client.get(key)
            if history:
                return json.loads(history)
        except redis.RedisError as e:
            logging.error(f"从Redis获取历史记录时出错: {e}")
        return []

    def save_history_to_redis(self, user_id, history):
        """将历史记录保存到Redis"""
        key = f"{self.redis_key_prefix}{user_id}"
        try:
            redis_client.set(key, json.dumps(history))
        except redis.RedisError as e:
            logging.error(f"保存历史记录到Redis时出错: {e}")

    def manage_history(self):
        """管理历史记录：删除最早的记录或截断字符长度"""
        self.history = self.get_history_from_redis(self.user_id)

        while len(self.history) > self.MAX_HISTORY_SIZE:
            self.history.pop(0)

        history_str = json.dumps(self.history)
        while len(history_str) > self.MAX_HISTORY_LENGTH:
            if self.history:
                self.history.pop(0)
                history_str = json.dumps(self.history)
            else:
                break

    async def run(self, user_name, query, user_id):
        try:
            # 从Redis获取历史记录并管理
            self.manage_history()

            # 添加用户输入到历史记录
            self.history.append({
                "Human": query,
            })

            # 调用格式化历史记录的方法
            history = self.format_history()

            # 生成结合用户输入和历史记录的输入
            combined_input = f"{query}\n用户id:{user_id}\n历史记录:\n {history}"

            logging.info(f"用户{user_name}的历史记录\n{history}")

            try:
                logging.info("使用gpt40-mini进行处理")
                # 调用AgentExecutor处理
                result = await asyncio.get_event_loop().run_in_executor(executor, lambda: self.agent_executor.invoke(
                    {"input": combined_input}))
            except Exception as e:  # 捕获特定的异常（如 RateLimitError），但此处使用 Exception 作为通用捕获
                logging.warning(f"gpt40-mini请求过多，切换到3.5-turbo处理。异常: {e}")
                # 备用 AgentExecutor 处理
                result = await asyncio.get_event_loop().run_in_executor(executor,
                                                                        lambda: self.agent_executor_substitute.invoke(
                                                                            {"input": combined_input}))

            output = result.get("output", "Error occurred")

            # 保存更新后的历史记录到Redis
            self.save_history_to_redis(self.user_id, self.history)

            return output
        except Exception as e:
            logging.error(f"运行时发生错误: {e}")
            traceback.print_exc()
            return "发生错误"
