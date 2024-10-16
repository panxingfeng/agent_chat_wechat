import asyncio
import logging
from datetime import datetime

import aiohttp
import pytz
from vchat import Core
from vchat.model import ContentTypes, ContactTypes

from config.config import LOGIN_WECHAT_DATA
from server.bot.chat_bot import ChatBot
from server.message.group.message import Group_message
from server.message.private.message import Private_message
from tools.else_tool.function import get_username_chatroom


# 创建日志器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 定义日志输出格式
formatter = logging.Formatter('[%(asctime)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

bot_name = LOGIN_WECHAT_DATA["name"]

# 初始化核心
core = Core()

# 定义北京时区
beijing_tz = pytz.timezone('Asia/Shanghai')

# 获取当前的 UTC 时间
current_utc_time = datetime.utcnow()

# 将 UTC 时间转换为北京时间
current_time = current_utc_time.astimezone(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

# 保存用户使用智能体状态
user_agent_status = {}

# 处理个人用户的消息
@core.msg_register(msg_types=ContentTypes.TEXT, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.ATTACH, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.IMAGE, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.VOICE, contact_type=ContactTypes.USER)
@core.msg_register(msg_types=ContentTypes.VIDEO, contact_type=ContactTypes.USER)
async def single_messages(msg):
    logging.info(f"接收到的消息类型{msg.content.type}")
    user_id = msg.from_.username
    user_name = msg.from_.nickname

    if user_name not in user_agent_status:
        user_agent_status[user_name] = False  # 默认不使用智能体

    if "#智能体" in msg.content.content:
        user_agent_status[user_name] = True
        await core.send_msg("成功设置智能体进行回复，输入 #聊天 切换为普通聊天模型(默认模式)", to_username=user_id)
        return
    elif "#聊天" in msg.content.content:
        user_agent_status[user_name] = False
        await core.send_msg("成功设置聊天模型进行回复", to_username=user_id)
        return
    
    message_handler = Private_message(
        user_id=user_id,
        user_name=user_name,
        core=core,
        bot_name=bot_name,
        current_time=current_time,
        logging=logging,
        use_agent=user_agent_status[user_name],  # 从字典获取是否使用智能体的状态
    )
    try:
        if msg.content.type == ContentTypes.TEXT:
            user_message = msg.content.content
            logging.info(f"开始处理用户【{user_name}】的文本消息: {user_message}")
            await asyncio.create_task(message_handler.handle_message(user_message=user_message))
            return

        elif msg.content.type == ContentTypes.IMAGE:
        #处理图像的消息逻辑
            return
        elif msg.content.type == ContentTypes.ATTACH:
        #处理文件的消息逻辑
            return
        elif msg.content.type == ContentTypes.VOICE:
        #处理音频的消息逻辑
            return
        elif msg.content.type == ContentTypes.VIDEO:
        #处理视频的消息逻辑
            return
        else:
            logging.warning(f"不支持的消息类型: {msg.content.type}")
            await core.send_msg(f"目前不支持的当前的消息类型: {msg.content.type}", to_username=msg.from_.username)
            return False

    except Exception as e:
        logging.error(f"处理消息时发生错误: {e}", exc_info=True)
        await core.send_msg(f"消息处理失败，请联系管理员进行修复\n问题原因: {e}", to_username=msg.from_.username)
        return False

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
        chatroom_name=chatroom_name
    )

    if msg.content.type == ContentTypes.TEXT:
        user_message = msg.content.content
        logging.info(f"开始处理微信群【{chatroom_name}】的用户【{user_name}】文本消息【 {user_message}】")
        bot = ChatBot(user_id=user_id, user_name=user_name)
        await asyncio.create_task(message_handler.handle_message(user_message=user_message, bot=bot))
    elif msg.content.type == ContentTypes.ATTACH:
        """处理文件的消息逻辑"""
    else:
        logging.warning(f"收到不支持的消息类型: {msg.content.type}")
        return False

    return True

# 主任务管理函数，确保各个任务并发执行
async def run_with_restart(task, max_retries=5, cooldown_time=5):
    retries = 0
    while True:
        try:
            await task()  # 执行传入的任务
        except Exception as e:
            retries += 1
            logging.error(f"任务执行时发生错误: {e}")
            logging.error("错误详情：", exc_info=True)

            if retries >= max_retries:
                logging.error(f"任务失败次数达到 {max_retries} 次，进入冷却时间 {cooldown_time} 秒")
                retries = 0
                await asyncio.sleep(cooldown_time)
            else:
                logging.info(f"重新动任务... 第 {retries} 次重启")
                await asyncio.sleep(1)

# 主任务调度
async def main_task():
    try:
        # 初始化核心功能
        await core.init()

        async with aiohttp.ClientSession():
            await core.auto_login(hot_reload=False)

            # 创建并行任务
            tasks = [
                asyncio.create_task(run_with_restart(core.run)),  # 运行核心功能的主循环
            ]

            await asyncio.gather(*tasks)

    except asyncio.CancelledError:
        logging.info("主程序取消，正在关闭所有任务...")
    except Exception as e:
        logging.error(f"启动时发生错误: {e}")
        logging.error("错误详情：", exc_info=True)
    finally:
        logging.info("程序退出。")

# 运行主程序
async def main():
    await main_task()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"主循环中发生错误: {e}")
        logging.error("错误详情：", exc_info=True)
