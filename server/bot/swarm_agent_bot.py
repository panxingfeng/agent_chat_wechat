import traceback
from swarm import Agent, Swarm
from config.config import OLLAMA_DATA, REDIS_DATA
from config.templates.data.bot import MAX_HISTORY_SIZE, MAX_HISTORY_LENGTH, AGENT_BOT_PROMPT_DATA, BOT_DATA, \
    CODE_BOT_PROMPT_DATA, SEARCH_BOT_PROMPT_DATA
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient
import logging
from datetime import datetime
import json
import redis
import asyncio
from concurrent.futures import ThreadPoolExecutor

from tools.swarm_tool.tool import code_gen,search_tool

# 设置日志记录
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# 初始化 Ollama 客户端
client = OllamaClient()
client_ollama = client.get_client()

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


class SwarmBot:
    def __init__(self, user_id, user_name, query):
        self.query = query
        self.user_name = user_name
        self.redis_key_prefix = "chat_history:"
        self.client = Swarm(client_ollama)
        self.history = []  # 自定义的历史记录列表
        self.saved_files = {}  # 保存文件路径的字典
        self.user_id = user_id
        self.instructions = AGENT_BOT_PROMPT_DATA.get("description").format(
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
        )

        self.agent = Agent(
            name="Bot Agent",
            instructions=self.instructions,
            functions=[self.transfer_to_code, self.transfer_to_search],  # 任务转发
            model=OLLAMA_DATA.get("model")
        )

        # 执行代码的智能体
        self.code_agent = Agent(
            name="Code Agent",
            instructions=CODE_BOT_PROMPT_DATA.get("description"),
            function=[code_gen],
            model=OLLAMA_DATA.get("model")
        )

        # 执行搜索的智能体
        self.search_agent = Agent(
            name="Search Agent",
            instructions=SEARCH_BOT_PROMPT_DATA.get("description").format(time=current_time),
            functions=[search_tool],
            model=OLLAMA_DATA.get("model")
        )

    # 跳转code智能体
    def transfer_to_code(self, query, code_type):
        print(f"使用的代码语言 {code_type} ,问题是 {query}")
        return self.code_agent
      
    # 跳转搜索智能体
    def transfer_to_search(self, query):
        print(f"使用网络资源以解决用户的问题:{query}")
        return self.search_agent
      
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
        global message

        try:
            # 从Redis获取历史记录并管理
            self.manage_history()

            # 添加用户输入到历史记录
            self.history.append({
                "Human": query,
            })

            # 调用格式化历史记录的方法
            history = self.format_history()

            messages = []
            # 生成结合用户输入和历史记录的输入
            combined_input = f"{query}\n用户id:{user_id}\n图像路径: {image_path}\n文件路径:{file_path}\n历史记录:\n {history}"
            messages.append({"role": "user", "content": combined_input})

            response = self.client.run(
                agent=self.agent,
                messages=messages,
                debug=True,
            )

            result = pretty_print_messages(response.messages)

            # # 将生成的回复加入历史记录
            # self.history.append({
            #     "AI": response,
            # })
            # 可以做保存也可以不做保存，保存提问的问题就可以满足很多需求

            # 保存更新后的历史记录到Redis
            self.save_history_to_redis(self.user_id, self.history)
            return result
        except Exception as e:
            logging.error(f"运行时发生错误: {e}")
            traceback.print_exc()
            return "发生错误"


def pretty_print_messages(messages) -> str:
    global message
    for message in messages:
        if message["role"] != "assistant":  # 只打印助手的回复
            continue

        # 蓝色显示智能体名称
        print(f"\033[94m{message['sender']}\033[0m:\n", end=" ")

        # 如果有工具调用，则打印工具调用的信息
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 0:
            print("\n调用的工具信息：")  # 提示工具调用信息
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]

            # 尝试将工具调用的参数格式化为 key=value 形式
            try:
                arg_str = json.dumps(json.loads(args), ensure_ascii=False, indent=2).replace(":", "=")
            except json.JSONDecodeError:
                arg_str = args  # 如果解析失败，原样显示

            # 紫色显示工具调用的函数名和参数
            print(f"  \033[95m{name}\033[0m({arg_str[1:-1]})")
    return message["content"]


if __name__ == "__main__":
    query = "使用代码工具，给我生成一份可执行的二叉树的python代码"
    user_id = "123"
    user_name = ""
    bot = SwarmBot(query=query, user_id=user_id, user_name=user_name)

    # 运行异步函数
    response = asyncio.run(bot.run(user_id=user_id, query=query, user_name=user_name, file_path=None, image_path=None))

    print(response)
