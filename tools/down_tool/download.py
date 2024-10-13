from pathlib import Path
from urllib.parse import unquote
import requests

def download_image(url, save_directory=None):
    try:
        # 获取图片的内容
        response = requests.get(url, timeout=20)  # 增加超时时间
        response.raise_for_status()  # 检查是否成功获取响应

        # 确保保存目录存在
        Path(save_directory).mkdir(parents=True, exist_ok=True)

        # 从 URL 提取并解码文件名
        file_name = unquote(url.split("/")[-1].split("?")[0])

        # 如果文件名没有扩展名，可以根据实际情况手动添加
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            # 从 response headers 获取内容类型
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
                file_name += '.png'  # 默认添加 .png 扩展名

        # 创建保存路径
        save_path = Path(save_directory) / file_name

        # 将图片的内容写入文件
        with open(save_path, "wb") as file:
            file.write(response.content)

        # 返回保存路径
        return save_path

    except requests.exceptions.RequestException as e:
        raise Exception(f"请求失败: {e}")
    except Exception as e:
        raise Exception(f"发生错误: {e}")


def download_audio(url, save_directory=None):
    try:
        # 获取音频内容
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 确保保存目录存在
            Path(save_directory).mkdir(parents=True, exist_ok=True)

            # 从 URL 提取并解码文件名
            file_name = unquote(url.split("/")[-1].split("?")[0])

            # 如果文件名没有扩展名，可以根据实际情况手动添加
            if not file_name.lower().endswith(('.wav', '.mp3', '.ogg', '.flac', '.aac')):
                file_name += '.wav'  # 默认添加 .wav 扩展名

            # 创建保存路径
            save_path = Path(save_directory) / file_name

            # 将音频内容写入文件
            with open(save_path, "wb") as file:
                file.write(response.content)

            # 返回保存路径
            return save_path
        else:
            raise Exception(f"Failed to download audio. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")
