import aiohttp
from sqlalchemy.testing.plugin.plugin_base import logging  # 这里的 logging 应该改为标准库中的 logging 模块

from PIL import Image
from io import BytesIO
import aiofiles
import mimetypes
import os

from tools.function import generate_random_filename


class ImageHandler:
    def __init__(self, save_directory):
        # 初始化 ImageHandler 类，指定保存图像的目录
        self.save_directory = save_directory

    async def save_image(self, image_data):
        """
        保存图像到指定目录
        :param image_data: 图像数据的字节流
        :return: 保存的文件路径，如果失败则返回 None
        """
        try:
            # 打开图像并验证其有效性
            image = Image.open(BytesIO(image_data))
            image.verify()

            # 如果目录不存在则创建
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成临时文件路径
            tmp_file_path = os.path.join(self.save_directory, generate_random_filename(extension=".png"))

            # 异步保存图像数据到文件
            async with aiofiles.open(tmp_file_path, 'wb') as tmp_file:
                await tmp_file.write(image_data)

            return tmp_file_path
        except Exception as e:
            logging.error(f"保存图像时出错: {e}")
            return None


class VoiceHandler:
    def __init__(self, save_directory):
        # 初始化 VoiceHandler 类，指定保存语音文件的目录
        self.save_directory = save_directory

    async def save_voice(self, audio_data, file_extension=".mp3"):
        """
        保存语音文件到指定目录
        :param audio_data: 语音数据的字节流
        :param file_extension: 文件扩展名，默认为 ".mp3"
        :return: 保存的文件路径，如果失败则返回 None
        """
        try:
            # 如果目录不存在则创建
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成文件名并创建文件路径
            file_name = generate_random_filename(extension=file_extension)
            file_path = os.path.join(self.save_directory, file_name)

            # 异步保存语音数据到文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)

            return file_path
        except Exception as e:
            logging.error(f"保存语音文件时出错: {e}")
            return None


class FileHandler:
    def __init__(self, save_directory):
        # 初始化 FileHandler 类，指定保存文件的目录
        self.save_directory = save_directory
        # 注册自定义 MIME 类型
        mimetypes.add_type('text/plain', '.log')

    async def save_file(self, file_data, file_name):
        """
        保存通用文件到指定目录
        :param file_data: 文件数据的字节流
        :param file_name: 文件名
        :return: 保存的文件路径，如果失败则返回 None
        """
        try:
            # 确定文件的 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_name)

            if not mime_type:
                logging.warning(f"无法确定文件的 MIME 类型，默认处理为通用文件: {file_name}")
                mime_type = 'application/octet-stream'

            # 如果目录不存在则创建
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成临时文件路径
            tmp_file_path = os.path.join(self.save_directory, file_name)

            # 根据 MIME 类型决定保存方法
            if not mime_type.startswith('image/'):
                await self._save_generic_file(file_data, tmp_file_path)
            else:
                raise ValueError("此方法不支持保存图像文件类型")

            return tmp_file_path
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")
            return None

    async def _save_generic_file(self, file_data, file_path):
        """
        保存通用文件的辅助方法
        :param file_data: 文件数据的字节流
        :param file_path: 文件保存路径
        """
        try:
            async with aiofiles.open(file_path, 'wb') as tmp_file:
                await tmp_file.write(file_data)
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")
            raise


class VideoDownloader:
    def __init__(self, save_directory):
        # 初始化 VideoDownloader 类，指定保存视频的目录
        self.save_directory = save_directory
        # 注册自定义 MIME 类型
        mimetypes.add_type('video/mp4', '.mp4')

    async def download_video(self, video_url, file_name):
        """
        从 URL 下载视频并保存到指定目录
        :param video_url: 视频的 URL
        :param file_name: 文件名
        :return: 保存的文件路径，如果失败则返回 None
        """
        try:
            # 确定文件的 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_name)

            if not mime_type:
                logging.warning(f"无法确定文件的 MIME 类型，默认处理为通用文件: {file_name}")
                mime_type = 'application/octet-stream'

            # 如果目录不存在则创建
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成临时文件路径
            tmp_file_path = os.path.join(self.save_directory, file_name)

            # 确保 MIME 类型为视频类型
            if not mime_type.startswith('video/'):
                raise ValueError("此方法仅支持保存视频文件类型")

            # 异步下载视频数据
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        video_data = await response.read()
                        await self._save_file(video_data, tmp_file_path)
                    else:
                        logging.error(f"下载视频失败，状态码: {response.status}")
                        return None

            return tmp_file_path
        except Exception as e:
            logging.error(f"下载视频时出错: {e}")
            return None

    async def _save_file(self, file_data, file_path):
        """
        保存文件的辅助方法
        :param file_data: 文件数据的字节流
        :param file_path: 文件保存路径
        """
        try:
            async with aiofiles.open(file_path, 'wb') as tmp_file:
                await tmp_file.write(file_data)
            logging.info(f"文件保存成功: {file_path}")
        except Exception as e:
            logging.error(f"保存文件时出错: {e}")
            raise
