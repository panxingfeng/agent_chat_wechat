import traceback
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.config import CHATGPT_DATA, REDIS_DATA
from config.templates.data.bot import MAX_HISTORY_SIZE, MAX_HISTORY_LENGTH, AGENT_BOT_PROMPT_DATA, BOT_DATA
import logging
from datetime import datetime
import json
import redis
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from tools.tool_loader import ToolLoader

# 初始化工具加载器
tool_loader = ToolLoader()
tool_loader.load_tools()  # 加载工具

# 获取加载的工具函数列表
tools = tool_loader.get_tools()

# 设置日志记录
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

os.environ["OPENAI_API_KEY"] = CHATGPT_DATA.get("key")
os.environ["OPENAI_API_BASE"] = CHATGPT_DATA.get("url")

# Redis 连接池
redis_pool = redis.ConnectionPool(host=REDIS_DATA.get("host"), port=REDIS_DATA.get("port"), db=REDIS_DATA.get("db"))
redis_client = redis.StrictRedis(connection_pool=redis_pool)

# 存储会话中的图像路径
user_image_map = {}

# 存储会话中的文件路径
user_file_map = {}

# 执行任务的线程池
executor = ThreadPoolExecutor(max_workers=20)

# 当前时间
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class AgentBot:
    def __init__(self, user_id, user_name, query):
        self.query = query
        self.user_name = user_name
        self.chatModel_4o_mini = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            streaming=True
        )
        self.redis_key_prefix = "chat_history:"
        self.history = []  # 自定义的历史记录列表
        self.saved_files = {}  # 保存文件路径的字典
        self.user_id = user_id
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    AGENT_BOT_PROMPT_DATA.get("description").format
                        (
                        name=BOT_DATA["agent"].get("name"),
                        capabilities=BOT_DATA["agent"].get("capabilities"),
                        welcome_message=BOT_DATA["agent"].get("default_responses").get("welcome_message"),
                        unknown_command=BOT_DATA["agent"].get("default_responses").get("unknown_command"),
                        language_support=BOT_DATA["agent"].get("language_support"),
                        current_time=current_time,
                        history=self.format_history(),
                        query=self.query,
                        user_name=self.user_name,
                        user_id=self.user_id
                    ),
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
            tools=tools,
            prompt=self.prompt
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
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

        while len(self.history) > MAX_HISTORY_SIZE:
            self.history.pop(0)

        history_str = json.dumps(self.history)
        while len(history_str) > MAX_HISTORY_LENGTH:
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

            result = await asyncio.get_event_loop().run_in_executor(executor, lambda: self.agent_executor.invoke(
                {"input": combined_input}))

            response = result.get("output", "Error occurred")

            # # 将生成的回复加入历史记录
            # self.history.append({
            #     "AI": response,
            # })
            # 可以做保存也可以不做保存，保存提问的问题就可以满足很多需求

            # 保存更新后的历史记录到Redis
            self.save_history_to_redis(self.user_id, self.history)

            return response
        except Exception as e:
            logging.error(f"运行时发生错误: {e}")
            traceback.print_exc()
            return "发生错误"

if __name__ == "__main__":
    query = "使用代码工具，给我生成一份可执行的二叉树的python代码"
    user_id = "123"
    user_name = ""
    bot = AgentBot(query=query, user_id=user_id, user_name=user_name)

    # 运行异步函数
    response = asyncio.run(bot.run(user_id=user_id, query=query, user_name=user_name, file_path=None, image_path=None))

    print(response)
