# 导入所需模块
from server.bot.agent_bot import *  # 引入自定义的agent_bot模块（假设是你项目中的部分）
from PIL import Image  # 用于图像处理
from io import BytesIO  # 用于处理二进制数据流
import aiofiles  # 用于异步文件操作
import mimetypes  # 用于猜测文件的 MIME 类型
import os  # 用于与操作系统交互（如创建目录）
from tools.else_tool.function import generate_random_filename  # 自定义函数，用于生成随机文件名

# 定义图像处理类
class ImageHandler:
    def __init__(self, save_directory):
        """
        初始化ImageHandler对象。

        :param save_directory: 图像保存的目录路径
        """
        self.save_directory = save_directory

    async def save_image(self, image_data):
        """
        异步保存图像数据到指定目录。

        :param image_data: 二进制图像数据
        :return: 保存的图像路径或None（出错时）
        """
        try:
            # 将二进制数据加载为PIL图像对象，并验证图像有效性
            image = Image.open(BytesIO(image_data))
            image.verify()

            # 如果保存目录不存在，则创建目录
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成随机文件名并构建完整路径
            file_name = await generate_random_filename(extension=".png")
            tmp_file_path = os.path.join(self.save_directory, file_name)

            # 异步写入图像数据到文件
            async with aiofiles.open(tmp_file_path, 'wb') as tmp_file:
                await tmp_file.write(image_data)

            return tmp_file_path
        except Exception as e:
            # 捕获并记录异常
            logging.error(f"保存图像时出错: {e}")
            return None


# 定义语音处理类
class VoiceHandler:
    def __init__(self, save_directory):
        """
        初始化VoiceHandler对象。

        :param save_directory: 语音文件保存的目录路径
        """
        self.save_directory = save_directory

    async def save_voice(self, audio_data, file_extension=".mp3"):
        """
        异步保存语音数据到指定目录。

        :param audio_data: 二进制语音数据
        :param file_extension: 语音文件的扩展名（默认.mp3）
        :return: 保存的文件路径或None（出错时）
        """
        try:
            # 如果保存目录不存在，则创建目录
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成随机文件名并构建完整路径
            file_name = await generate_random_filename(extension=file_extension)
            file_path = os.path.join(self.save_directory, file_name)

            # 异步写入语音数据到文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)

            return file_path
        except Exception as e:
            # 捕获并记录异常
            logging.error(f"保存语音文件时出错: {e}")
            return None


# 定义文件处理类
class FileHandler:
    def __init__(self, save_directory):
        """
        初始化FileHandler对象。

        :param save_directory: 文件保存的目录路径
        """
        self.save_directory = save_directory
        # 添加自定义的MIME类型（日志文件类型）
        mimetypes.add_type('text/plain', '.log')

    async def save_file(self, file_data, file_name):
        """
        异步保存通用文件到指定目录。

        :param file_data: 二进制文件数据
        :param file_name: 文件名称
        :return: 保存的文件路径或None（出错时）
        """
        try:
            # 根据文件名猜测MIME类型
            mime_type, _ = mimetypes.guess_type(file_name)

            if not mime_type:
                # 如果无法确定MIME类型，则设置为默认的二进制流类型
                logging.warning(f"无法确定文件的 MIME 类型，默认处理为通用文件: {file_name}")
                mime_type = 'application/octet-stream'

            # 如果保存目录不存在，则创建目录
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 构建保存文件的完整路径
            tmp_file_path = os.path.join(self.save_directory, file_name)

            # 如果文件不是图像类型，则保存为通用文件
            if not mime_type.startswith('image/'):
                await self._save_generic_file(file_data, tmp_file_path)
            else:
                # 如果文件类型是图像，抛出异常
                raise ValueError("此方法不支持保存图像文件类型")

            return tmp_file_path
        except Exception as e:
            # 捕获并记录异常
            logging.error(f"保存文件时出错: {e}")
            return None

    async def _save_generic_file(self, file_data, file_path):
        """
        辅助方法：异步保存通用文件。

        :param file_data: 二进制文件数据
        :param file_path: 保存的文件路径
        """
        try:
            # 异步写入文件数据到文件
            async with aiofiles.open(file_path, 'wb') as tmp_file:
                await tmp_file.write(file_data)
        except Exception as e:
            # 捕获并记录异常，并重新抛出
            logging.error(f"保存文件时出错: {e}")
            raise


# 定义视频处理类
class VideoHandler:
    def __init__(self, save_directory):
        """
        初始化VideoHandler对象。

        :param save_directory: 视频文件保存的目录路径
        """
        self.save_directory = save_directory
        # 添加自定义的MIME类型（MP4视频类型）
        mimetypes.add_type('video/mp4', '.mp4')

    async def save_video(self, video_data):
        """
        异步保存视频数据到指定目录。

        :param video_data: 二进制视频数据
        :return: 保存的文件路径或None（出错时）
        """
        try:
            # 如果保存目录不存在，则创建目录
            if not os.path.exists(self.save_directory):
                os.makedirs(self.save_directory)

            # 生成随机文件名并构建完整路径
            file_name = await generate_random_filename(extension=".mp4")
            tmp_file_path = os.path.join(self.save_directory, file_name)

            # 异步写入视频数据到文件
            async with aiofiles.open(tmp_file_path, 'wb') as tmp_file:
                await tmp_file.write(video_data)

            logging.info(f"视频保存成功: {tmp_file_path}")
            return tmp_file_path

        except Exception as e:
            # 捕获并记录异常
            logging.error(f"保存视频时出错: {e}")
            return None
