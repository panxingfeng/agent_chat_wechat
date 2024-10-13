from server.bot.agent_bot import *
from PIL import Image
from io import BytesIO
import aiofiles
import mimetypes
import os

from tools.else_tool.function import generate_random_filename


class ImageHandler:
    def __init__(self, save_directory):
        self.save_directory = save_directory

    async def save_image(self, image_data):
        try:
            image = Image.open(BytesIO(image_data))
            image.verify()

            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            file_name = await generate_random_filename(extension=".png")
            tmp_file_path = os.path.join(self.save_directory, file_name)

            async with aiofiles.open(tmp_file_path, 'wb') as tmp_file:
                await tmp_file.write(image_data)

            return tmp_file_path
        except Exception as e:
            logging.error(f"保存图像时出错: {e}")
            return None


class VoiceHandler:
    def __init__(self, save_directory):
        self.save_directory = save_directory

    async def save_voice(self, audio_data, file_extension=".mp3"):
        try:
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            file_name = await generate_random_filename(extension=file_extension)
            file_path = os.path.join(self.save_directory, file_name)

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)

            return file_path
        except Exception as e:
            logging.error(f"保存语音文件时出错: {e}")
            return None


class FileHandler:
    def __init__(self, save_directory):
        self.save_directory = save_directory
        mimetypes.add_type('text/plain', '.log')

    async def save_file(self, file_data, file_name):
        try:
            mime_type, _ = mimetypes.guess_type(file_name)

            if not mime_type:
                logging.warning(f"无法确定文件的 MIME 类型，默认处理为通用文件: {file_name}")
                mime_type = 'application/octet-stream'

            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            tmp_file_path = os.path.join(self.save_directory, file_name)

            if not mime_type.startswith('image/'):
                await self._save_generic_file(file_data, tmp_file_path)
            else:
                raise ValueError("此方法不支持保存图像文件类型")

            return tmp_file_path
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")
            return None

    async def _save_generic_file(self, file_data, file_path):
        try:
            async with aiofiles.open(file_path, 'wb') as tmp_file:
                await tmp_file.write(file_data)
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")
            raise


class VideoHandler:
    def __init__(self, save_directory):
        self.save_directory = save_directory
        # 增加对 MP4 文件的 MIME 类型支持
        mimetypes.add_type('video/mp4', '.mp4')

    async def save_video(self, video_data):
        """保存视频数据到本地并返回文件路径"""
        try:
            # 检查并创建保存目录
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成随机文件名并保存视频
            file_name = await generate_random_filename(extension=".mp4")
            tmp_file_path = os.path.join(self.save_directory, file_name)

            async with aiofiles.open(tmp_file_path, 'wb') as tmp_file:
                await tmp_file.write(video_data)

            logging.info(f"视频保存成功: {tmp_file_path}")
            return tmp_file_path

        except Exception as e:
            logging.error(f"保存视频时出错: {e}")
            return None

