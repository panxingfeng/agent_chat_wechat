import logging
import os
import re
import mysql.connector

from vchat import Core

from config.config import DOWNLOAD_ADDRESS, GROUP_DATA, LOGIN_WECHAT_DATA, DB_DATA
from server.bot.agent_bot import user_image_map, Agent_Bot
from server.bot.chat_bot import Chat_Bot
from tools.down_tool.handler import ImageHandler, VoiceHandler, FileHandler
from tools.else_tool.function import extract_game_name
from user.user import extract_user_info

# 保存用户的激活码状态，包括剩余时间和当天的验证状态
user_activation_status = {}

# 保存用户名和文件路径的映射
user_file_mapping = {}

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    'url': "",
    'pdf': "",
    'docx': "",
    'excel': "",
    'csv': "",
    'md': "",
}

core = Core()

connection = mysql.connector.connect(
        host=DB_DATA.get("host"),
        user=DB_DATA.get("user"),
        password=DB_DATA.get("password"),
        database=DB_DATA.get("database")
    )

class Group_message:
    def __init__(self, user_id, user_name, core, bot_name, current_time, logging, chatroom_name):
        self.game = None
        self.user_id = user_id
        self.user_name = user_name
        self.core = core
        self.bot_name = bot_name
        self.connection = connection
        self.current_time = current_time
        self.logging = logging
        self.chatroom_name = chatroom_name
        self.agent_bot = Agent_Bot(query=None, user_id=user_id, user_name=user_name)
        self.chat_bot = Chat_Bot()
        self.image_handler = ImageHandler(save_directory=DOWNLOAD_ADDRESS.get("image"))
        self.voice_handler = VoiceHandler(save_directory=DOWNLOAD_ADDRESS.get("audio"))
        self.file_handler = FileHandler(save_directory=DOWNLOAD_ADDRESS.get("file"))

    async def handle_message(self, user_message, bot):
        """处理收到的消息"""
        self.logging.info(f"收到了群【{self.chatroom_name}】的用户【{self.user_name}】的消息【{user_message}】")
        await self.distribute_message(user_message, bot)

    async def distribute_message(self, user_message, bot):
        """消息的分发"""
        user_message = user_message.strip()
        user_message = re.sub(r'\s+', ' ', user_message)  # 处理多余空格
        print(f"user_message: {repr(user_message)}")  # 打印消息进行检查

        if "-h" in user_message:
            reply_message = GROUP_DATA.get('chatroom-h')
            await self.core.send_msg(1, reply_message, to_username=self.user_id)
            return

        await self.message_analysis(user_message, bot)

        if f"@{self.bot_name}" in user_message:
            await self.message_analysis(user_message, bot)
            if re.match(r'^p\b', user_message, re.IGNORECASE):
                await self.handle_image_message()
            elif re.match(r'^q\b', user_message, re.IGNORECASE):
                await self.handle_question_message(user_message, bot)
            else:
                await self.handle_else_message(user_message, bot)

    async def message_analysis(self, user_message, bot):
        """分析消息是否包含敏感词"""

    async def handle_image_message(self):
        """处理图像的信息"""

    async def handle_else_message(self, user_message, bot):
        self.logging.info(f"提取到的用户信息:{extract_user_info(self.user_name)}")
        reply_content = self.chat_bot.run(
            user_name=self.user_name,
            query=user_message
        )
        await self.core.send_msg(f"@{self.user_name} {reply_content}", to_username=self.user_id)
        return True

    async def handle_question_message(self, user_message, bot):
        """处理问题的消息"""

    async def save_file_message_to_local(self, file_name, file_path):
        """把文件保存到本地"""
