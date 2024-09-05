import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from logging.handlers import RotatingFileHandler

import aiohttp
from vchat.model import ContentTypes, ContactTypes
from vchat import Core

from bot.chatBot_agent import Chat_Bot_Agent
from bot.chatBot_chat import Chat_Bot_Chat
from message.group.message import Group_message
from message.private.message import Private_message
from tools.function import get_username_chatroom

# 创建日志器
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # 设置全局日志级别

# 日志输出格式
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d]: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# 文件日志处理器，带日志轮转功能（最大5MB，保留3个备份）
file_handler = RotatingFileHandler('error.log', maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.ERROR)  # 设置文件日志的级别为 ERROR
file_handler.setFormatter(formatter)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 设置控制台日志级别为 DEBUG
console_handler.setFormatter(formatter)

# 将处理器添加到日志器
logger.addHandler(file_handler)
logger.addHandler(console_handler)


base_dir = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(base_dir, "./config/config.json")
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

bot_name = config['bot_name']

# 初始化核心
core = Core()

# 创建任务的线程池
thread_pool = ThreadPoolExecutor(max_workers=50)


current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 处理个人用户的消息
@core.msg_register(msg_types=ContentTypes.TEXT, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.IMAGE, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.VOICE, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.ATTACH, contact_type=ContactTypes.USER)
async def single_messages(msg):
    user_id = msg.from_.username
    user_name = msg.from_.nickname

    message_handler = Private_message(
        user_id=user_id,
        user_name=user_name,
        core=core,
        bot_name=bot_name,
        current_time=current_time,
        logging=logging,
    )

    try:
        # 检查消息类型
        logging.info(f"接收到来自用户【{user_name}】的消息类型: {msg.content.type}")

        if msg.content.type == ContentTypes.TEXT:
            if config["agent"]:
                user_message = msg.content.content
                bot = Chat_Bot_Agent(user_name=user_name, user_id=user_id)
                logging.info(f"开始处理用户【{user_name}】的文本消息: {user_message}")
                asyncio.create_task(message_handler.handle_message(user_message=user_message, bot=bot))
            else:
                user_message = msg.content.content
                bot = Chat_Bot_Chat(user_name=user_name,user_id=user_id)
                logging.info(f"开始处理用户【{user_name}】的文本消息: {user_message}")
                asyncio.create_task(message_handler.handle_message(user_message=user_message, bot=bot))
        else:
            logging.warning(f"不支持的消息类型: {msg.content.type}")
            await core.send_msg( f"目前不支持的当前的消息类型: {msg.content.type}", to_username=msg.from_.username)
            return False

    except Exception as e:
        logging.error(f"处理消息时发生错误: {e}", exc_info=True)
        await core.send_msg(f"消息处理失败，请联系管理员进行修复\n问题原因: {e}", to_username=msg.from_.username)
        return False

    return True

# 处理群聊中的消息
@core.msg_register(msg_types=ContentTypes.ATTACH, contact_type=ContactTypes.CHATROOM)
@core.msg_register(msg_types=ContentTypes.TEXT, contact_type=ContactTypes.CHATROOM)
async def chatroom_messages(msg):
    chatroom_name = getattr(msg.from_, 'nickname', None)
    user_id = getattr(msg.from_, 'username', None)
    user_name = get_username_chatroom(str(getattr(msg, 'chatroom_sender', None)))

    message_handler = Group_message(
        user_id=user_id,
        user_name=user_name,
        core=core,
        bot_name=bot_name,
        current_time=current_time,
        logging=logging,
        chatroom_name=chatroom_name)

    if msg.content.type == ContentTypes.TEXT:
        user_message = msg.content.content
        logging.info(f"开始处理微信群【{chatroom_name}】的用户【{user_name}】文本消息【 {user_message}】")
        bot = Chat_Bot_Chat(user_name=user_name,user_id=user_id)
        asyncio.create_task(message_handler.handle_message(user_message=user_message,bot=bot))
    else:
        logging.warning(f"收到不支持的消息类型: {msg.content.type}")
        return False

    return True

async def run_with_restart(task):
    """如果任务发生异常，将会重新启动任务"""
    while True:
        try:
            await task()  # 执行传入的任务
        except Exception as e:
            logging.error(f"任务执行时发生错误: {e}")
            logging.error("错误详情：", exc_info=True)
            logging.info("重新启动任务...")
            await asyncio.sleep(1)  # 延迟一秒后重新启动任务

async def main_task():
    global thread_pool, scheduler
    session = None
    try:
        # 初始化核心功能
        await core.init()
        session = aiohttp.ClientSession()  # 创建 aiohttp 会话
        await core.auto_login(hot_reload=False)  # 执行自动登录


        # 创建并行任务
        tasks = [
            asyncio.create_task(run_with_restart(core.run)),  # 运行核心功能的主循环
        ]

        await asyncio.gather(*tasks)

    except asyncio.CancelledError:
        logging.info("主程序取消，正在关闭所有任务...")
    except NotImplementedError as nie:
        logging.error(f"捕获到未实现的功能错误: {nie}")
        logging.error("可能是在处理群聊消息时发生了错误，请检查相关功能实现。")
    except Exception as e:
        logging.error(f"启动时发生错误: {e}")
        logging.error("错误详情：", exc_info=True)
    finally:
        # 确保资源被正确关闭
        if session and not session.closed:
            await session.close()  # 确保关闭 aiohttp 会话
        logging.info("已关闭客户端会话，程序继续运行。")

async def main():
    await main_task()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"主循环中发生错误: {e}")
        logging.error("错误详情：", exc_info=True)
