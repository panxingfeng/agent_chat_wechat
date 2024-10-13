import re
from pathlib import Path

import requests

from config.config import DOWNLOAD_ADDRESS, PRIVATE_DATA
from server.bot.chat_bot import Chat_Bot_Chat
from tools.down_tool.download import download_audio, download_image

from tools.down_tool.handler import *
from tools.else_tool.function import clean_latex_content, get_url, save_message_to_mysql, upload_pdf_to_server
from user.user import *

from server.bot.agent_bot import Agent_Bot, user_image_map
from tools.down_tool.handler import VideoHandler, FileHandler, VoiceHandler, ImageHandler
from user.user import save_user_id

# 保存用户的激活码状态，包括剩余时间和当天的验证状态
user_activation_status = {}

# 保存用户名和文件路径的映射
user_file_mapping = {}

# 存储每个用户发送的多张图片
user_images_map = {}

# 存储每个用户发送的多视频
user_videos_map = {}

# 追踪用户是否已经发送过问题
user_question_status = {}

# 执行任务的线程池
executor = ThreadPoolExecutor(max_workers=100)

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    'url': "",
    'pdf': "",
    'docx': "",
    'excel': "",
    'csv': "",
    'md': "",
}


class Private_message:
    def __init__(self, user_id, user_name, core, bot_name, current_time, logging, use_agent):
        self.user_id = user_id
        self.user_name = user_name
        self.core = core
        self.bot_name = bot_name
        self.current_time = current_time
        self.logging = logging
        self.use_agent = use_agent
        self.agent_bot = Agent_Bot(query=None, user_id=user_id, user_name=user_name)
        self.chat_bot = Chat_Bot_Chat(user_id=user_id, user_name=user_name)
        self.image_handler = ImageHandler(save_directory=DOWNLOAD_ADDRESS.get("image"))
        self.voice_handler = VoiceHandler(save_directory=DOWNLOAD_ADDRESS.get("audio"))
        self.file_handler = FileHandler(save_directory=DOWNLOAD_ADDRESS.get("file"))
        self.vidio_handler = VideoHandler(save_directory=DOWNLOAD_ADDRESS.get("vidio"))

    async def handle_message(self, user_message):
        """处理接受到的消息"""
        save_user_id(user_id=self.user_id, user_name=self.user_name)
        await self.distribute_message(user_message)

    async def distribute_message(self, user_message):
        """消息的分发"""
        user_message = user_message.strip()
        result = await self.check_activation_code(user_message)
        if "-h" in user_message:
            reply_message = PRIVATE_DATA.get('single-h')
            await self.core.send_msg(reply_message, to_username=self.user_id)
            return
        if result:
            if re.match(r'^p\b', user_message, re.IGNORECASE):
                await self.handle_image_message(user_message)
                return
            elif re.match(r'^q\b', user_message, re.IGNORECASE):
                await self.handle_file_message(user_message)
                return
            elif re.match(r'^v\b', user_message, re.IGNORECASE):
                await self.handle_video_message(user_message)
                return
            else:
                await self.handle_text_message(user_message)
                return

    async def handle_image_message(self, user_message):
        """处理图像的问题"""

    async def handle_file_message(self, user_message):
        """处理关于文件问答的问题"""

    async def handle_video_message(self, user_message):
        """处理视频的问题"""

    async def send_message_type(self, reply_message):
        if reply_message is None:
            await self.core.send_msg(f"回复内容生成错误，请联系管理员", to_username=self.user_id)
            return
        if ".png" in reply_message:
            link = get_url(reply_message)
            file = download_image(link)
            file_path = Path(file)
            await self.core.send_msg(f"这是您生成的图像", to_username=self.user_id)
            await self.core.send_image(to_username=self.user_id, file_path=file_path)
            return
        elif ".wav" in reply_message:
            link = get_url(reply_message)
            file = download_audio(link)
            file_path = Path(file)
            await self.core.send_msg(f"这是生成的语音信息", to_username=self.user_id)
            await self.core.send_file(to_username=self.user_id, file_path=file_path)
            return
        else:
            await self.core.send_msg(reply_message, to_username=self.user_id)

    async def handle_text_message(self, user_message):
        """处理关于文本内容的消息"""
        global reply_content
        if self.use_agent:
            await self.core.send_msg("智能体开始处理...", to_username=self.user_id)
            reply_content = self.agent_bot.run(
                user_name=self.user_name,
                query=user_message,
                image_path=user_image_map.get(self.user_id),
                file_path=user_file_mapping.get(self.user_name),
                user_id=self.user_id
            )
        else:
            reply_content = self.chat_bot.run(
                user_name=self.user_name,
                query=user_message
            )
        await self.send_message_type(reply_content)
        return

    async def save_message_to_mysql(self, reply_content):
        """保存用户的内容到数据库中"""

    async def save_image_message_to_local(self, file_path):
        """保存用户的图像到本地路径，并根据用户的操作状态删除之前的图像"""

    async def save_file_message_to_local(self, file_name, file_path):
        """保存用户的文件到本地路径"""

    async def save_video_message_to_local(self, file_path):
        """保存用户的视频到本地路径，并根据用户的操作状态删除之前的视频"""

    async def handle_voice_message(self,file_path):
        """保存用户的音频到本地路径，检测当前是否支持cuda设备来处理语音消息，并使用音频进行回复"""
