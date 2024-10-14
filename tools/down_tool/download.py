# 导入所需模块
from pathlib import Path  # 用于操作文件和目录路径
from urllib.parse import unquote  # 用于解码URL中的特殊字符
import requests  # 用于发送HTTP请求

def download_image(url, save_directory=None):
    """
    下载图像并将其保存到指定目录。

    :param url: 要下载的图像的URL
    :param save_directory: 保存图像的目录路径（默认为None）
    :return: 保存图像的路径
    :raises: Exception 当请求失败或其他错误发生时抛出异常
    """
    try:
        # 获取图像内容，设置超时时间为20秒
        response = requests.get(url, timeout=20)
        response.raise_for_status()  # 检查是否成功获取响应，否则抛出HTTPError

        # 确保保存目录存在，如果不存在则创建
        Path(save_directory).mkdir(parents=True, exist_ok=True)

        # 从URL提取文件名并解码特殊字符
        file_name = unquote(url.split("/")[-1].split("?")[0])

        # 检查文件名是否具有常见的图像扩展名
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            # 根据响应头的Content-Type字段来确定图像类型
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                file_name += '.png'
            elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
                file_name += '.jpg'
            elif 'image/gif' in content_type:
                file_name += '.gif'
            elif 'image/bmp' in content_type:
                file_name += '.bmp'
            elif 'image/webp' in content_type:
                file_name += '.webp'
            else:
                # 如果无法确定类型，默认使用.png扩展名
                file_name += '.png'

        # 创建保存图像的完整路径
        save_path = Path(save_directory) / file_name

        # 将图像内容写入文件
        with open(save_path, "wb") as file:
            file.write(response.content)

        # 返回图像的保存路径
        return save_path

    except requests.exceptions.RequestException as e:
        # 捕获并抛出请求异常
        raise Exception(f"请求失败: {e}")
    except Exception as e:
        # 捕获并抛出所有其他异常
        raise Exception(f"发生错误: {e}")

def download_audio(url, save_directory=None):
    """
    下载音频文件并将其保存到指定目录。

    :param url: 要下载的音频文件的URL
    :param save_directory: 保存音频的目录路径（默认为None）
    :return: 保存音频文件的路径
    :raises: Exception 当请求失败或其他错误发生时抛出异常
    """
    try:
        # 获取音频内容
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 确保保存目录存在，如果不存在则创建
            Path(save_directory).mkdir(parents=True, exist_ok=True)

            # 从URL提取文件名并解码特殊字符
            file_name = unquote(url.split("/")[-1].split("?")[0])

            # 检查文件名是否具有常见的音频扩展名
            if not file_name.lower().endswith(('.wav', '.mp3', '.ogg', '.flac', '.aac')):
                # 如果没有有效扩展名，默认使用.wav扩展名
                file_name += '.wav'

            # 创建保存音频的完整路径
            save_path = Path(save_directory) / file_name

            # 将音频内容写入文件
            with open(save_path, "wb") as file:
                file.write(response.content)

            # 返回音频的保存路径
            return save_path
        else:
            # 如果请求不成功，抛出异常并包含状态码信息
            raise Exception(f"Failed to download audio. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        # 捕获并抛出请求异常
        raise Exception(f"Request failed: {e}")
    except Exception as e:
        # 捕获并抛出所有其他异常
        raise Exception(f"An error occurred: {e}")
