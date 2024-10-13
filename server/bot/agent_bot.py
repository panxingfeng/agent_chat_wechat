import traceback
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_openai import ChatOpenAI

from configs.config import CHATGPT_DATA, DB_DATA
from tools.tool_loader import ToolLoader
import logging
from datetime import datetime
import json
import redis
import asyncio
import os
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

# 设置日志记录
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

os.environ["OPENAI_API_KEY"] = CHATGPT_DATA.get("key")
os.environ["OPENAI_API_BASE"] = CHATGPT_DATA.get("url")

# 设置 MySQL 连接池
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host=DB_DATA.get("host"),
    user=DB_DATA.get("user"),
    password=DB_DATA.get("password"),
    database=DB_DATA.get("database")
)

# 初始化工具加载器
tool_loader = ToolLoader()
tool_loader.load_tools()  # 加载工具

# 获取加载的所有工具
loaded_tools = tool_loader.get_tools()

# # 配置音频处理工具
# AudioSegment.converter = "E:/ProgramData/ffmpeg/bin/ffmpeg.exe"
# AudioSegment.ffprobe = "E:/ProgramData/ffmpeg/bin/ffprobe.exe"

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


class Agent_Bot:
    MAX_HISTORY_SIZE = 6
    MAX_HISTORY_LENGTH = 500
    conn = pool.get_connection()

    def __init__(self, user_id, user_name,query):
        self.query = query
        self.user_name = user_name
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
        self.redis_key_prefix = "chat_history:"
        self.history = []  # 自定义的历史记录列表
        self.saved_files = {}  # 保存文件路径的字典
        self.user_id = user_id
        self.SYSTEMPL = """
        你是一个智能化的全能机器人，姓名：小pan，是由PanllQ开发者开发为用户服务，你具备广泛的知识和实时数据处理能力。

        ### 历史记录:
        {history}

        ### 当前时间:
        {current_time}

        ### 用户问题:
        {query}

        ### 用户id:
        {user_id}

        ### 用户名:
        {user_name}
        """
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.SYSTEMPL.format(current_time=current_time, history=self.format_history(), query=self.query,
                                         user_name=self.user_name, user_id=self.user_id),
                ),
                (
                    "user",
                    "{input}"
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )

        agent = create_openai_tools_agent(
            self.chatModel_4o_mini,
            tools=loaded_tools,
            prompt=self.prompt
        )

        agent_substitute = create_openai_tools_agent(
            self.chatModel_3_5,
            tools=loaded_tools,
            prompt=self.prompt
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=loaded_tools,
            verbose=True
        )
        self.agent_executor_substitute = AgentExecutor(
            agent=agent_substitute,
            tools=loaded_tools,
            verbose=True
        )

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
        """管理历史记录：删除最早de记录或截断字符长度"""
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

    async def run(self, user_name, query, image_path, file_path, user_id):
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
            combined_input = f"{query}\n用户id:{user_id}\n图像路径: {image_path}\n文件路径:{file_path}\n历史记录:\n {history}"

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