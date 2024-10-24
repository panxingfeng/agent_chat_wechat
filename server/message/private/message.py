import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

from pathlib import Path
from config.config import DOWNLOAD_ADDRESS, OLLAMA_DATA, CHATGPT_DATA
from config.templates.data.bot import PRIVATE_DATA
from server.bot.agent_bot import user_image_map
from server.bot.chat_bot import ChatBot

from tools.down_tool.download import download_audio, download_image

from tools.else_tool.function import get_url

from tools.down_tool.handler import VideoHandler, FileHandler, VoiceHandler, ImageHandler

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
        self.chat_bot = ChatBot(user_id=user_id, user_name=user_name)
        self.image_handler = ImageHandler(save_directory=DOWNLOAD_ADDRESS.get("image"))
        self.voice_handler = VoiceHandler(save_directory=DOWNLOAD_ADDRESS.get("audio"))
        self.file_handler = FileHandler(save_directory=DOWNLOAD_ADDRESS.get("file"))
        self.vidio_handler = VideoHandler(save_directory=DOWNLOAD_ADDRESS.get("vidio"))

    async def handle_message(self, user_message):
        """处理接受到的消息"""
        global bot
        if self.use_agent:
            await self.core.send_msg("智能体开始处理...", to_username=self.user_id)
            if CHATGPT_DATA.get("use"):
                from server.bot.agent_bot import AgentBot
                bot = AgentBot(query=None, user_id=self.user_id, user_name=self.user_name)
            elif OLLAMA_DATA.get("use"):
                from server.bot.swarm_agent_bot import SwarmBot
                bot = SwarmBot(query=None, user_id=self.user_id, user_name=self.user_name)
        else:
            bot = self.chat_bot
        await self.distribute_message(user_message, bot)

    async def distribute_message(self, user_message, bot):
        """消息的分发"""
        user_message = user_message.strip()
        result = True  # 可以增加对用户账号使用权的确认
        if "-h" in user_message:
            reply_message = PRIVATE_DATA.get('single-h')
            await self.core.send_msg(reply_message, to_username=self.user_id)
            return
        if result:
            if re.match(r'^p\b', user_message, re.IGNORECASE):
                await self.handle_image_message(user_message, bot)
                return
            elif re.match(r'^q\b', user_message, re.IGNORECASE):
                await self.handle_file_message(user_message, bot)
                return
            elif re.match(r'^v\b', user_message, re.IGNORECASE):
                await self.handle_video_message(user_message, bot)
                return
            else:
                await self.handle_text_message(user_message, bot)
                return
        else:
            await self.core.send_msg("账户无法使用", to_username=self.user_id)

    async def handle_image_message(self, user_message, bot):
        # 处理图像的问题
        return

    async def handle_file_message(self, user_message, bot):
        # 处理关于文件问答的问题
        return

    async def handle_video_message(self, user_message, bot):
        # 处理视频的问题
        return

    async def send_message_type(self, reply_message):
        # 确保 reply_message 是实际结果
        if asyncio.iscoroutine(reply_message):
            reply_message = await reply_message

        if reply_message is None:
            await self.core.send_msg("回复内容生成错误，请联系管理员", to_username=self.user_id)
            return

        # 处理图像消息
        if ".png" in reply_message:
            link = get_url(reply_message)
            file = download_image(link)
            file_path = Path(file)

            await self.core.send_msg("这是您生成的图像", to_username=self.user_id)
            await self.core.send_image(to_username=self.user_id, file_path=file_path)
            return

        # 处理语音消息
        elif ".wav" in reply_message:
            link = get_url(reply_message)
            file = download_audio(link)
            file_path = Path(file)

            await self.core.send_msg("这是生成的语音信息", to_username=self.user_id)
            await self.core.send_file(to_username=self.user_id, file_path=file_path)
            return

        # 处理文本消息
        else:
            await self.core.send_msg(reply_message, to_username=self.user_id)

    async def handle_text_message(self, user_message, bot):
        """处理关于文本内容的消息"""
        global reply_content
        reply_content = await bot.run(
            user_name=self.user_name,
            query=user_message,
            image_path=user_image_map.get(self.user_id),
            file_path=user_file_mapping.get(self.user_name),
            user_id=self.user_id
        )
        print(reply_content)
        await self.send_message_type(reply_content)
        return

    async def save_message_to_mysql(self, reply_content):
        # 保存用户的内容到数据库中
        return

    async def save_image_message_to_local(self, file_path):
        # 保存用户的图像到本地路径，并根据用户的操作状态删除之前的图像
        return

    async def save_file_message_to_local(self, file_name, file_path):
        # 保存用户的文件到本地路径
        return

    async def save_video_message_to_local(self, file_path):
        # 保存用户的视频到本地路径，并根据用户的操作状态删除之前的视频
        return

    async def handle_voice_message(self, file_path):
        # 保存用户的音频到本地路径，检测当前是否支持cuda设备来处理语音消息，并使用音频进行回复
        return
