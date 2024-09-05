import logging
import os
import json
import requests
from langchain.agents import tool

logging.basicConfig(level=logging.INFO)

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "../config/config.json")
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

@tool
def search_music(music_name: str) -> str:
    """搜索音乐资源的工具"""

    base_url = "https://papi.oxoll.cn/API/music/api.php"
    params = {
        "music": music_name,
        "type": "netease"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        music_data = response.json()

        if music_data and "data" in music_data:
            results = music_data["data"]
            response_message = f"搜索到 {len(results)} 条结果:\n"
            for result in results:
                response_message += (
                    f"\n歌曲名称: {result['title']}\n"
                    f"作者: {result['author']}\n"
                    f"播放链接: {result['url']}\n"
                    f"封面图片链接: {result['pic']}\n"
                    f"{'-' * 40}\n"
                )
            return response_message
        else:
            return "未找到相关音乐资源。"

    except requests.exceptions.RequestException as e:
        return f"请求失败：{e}"


@tool
def fetch_60s_report() -> list:
    """搜索并返回60秒早报的内容"""

    ollama_url = 'https://api.52vmy.cn/api/wl/60s/new'

    try:
        # 发送HTTP GET请求，禁用代理
        response = requests.get(ollama_url, proxies={"http": None, "https": None})
        response.raise_for_status()

        response.encoding = 'utf-8'
        data = response.json()

        # 检查请求是否成功
        if data.get('code') == 200:
            # 返回data中的内容
            return data.get('data', [])
        else:
            print(f"请求成功但返回数据异常，错误消息: {data.get('msg')}")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"请求错误发生: {err}")
        return []


@tool
def fetch_history_today() -> dict:
    """获取历史上的今天事件信息，并返回url、title和日期"""

    api_url = f'https://cn.apihz.cn/api/zici/today.php?id=88888888&key=88888888'

    try:
        response = requests.get(api_url, proxies={"http": None, "https": None})
        response.raise_for_status()

        data = response.json()

        # 检查请求是否成功
        if data.get('code') == 200:
            # 提取所需的信息
            result = {
                "title": data.get('title'),
                "url": data.get('url'),
                "date": f"{data.get('y')}-{data.get('m').zfill(2)}-{data.get('d').zfill(2)}"
            }
            return result
        else:
            print(f"请求成功但返回数据异常，错误消息: {data.get('msg')}")
            return {}

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
        return {}
    except requests.exceptions.RequestException as err:
        print(f"请求错误发生: {err}")
        return {}


@tool
def generate_qr_code(text: str) -> str:
    """生成二维码并返回二维码图片的URL"""

    # 警告信息：检查并替换&符号
    if '&' in text:
        print("警告: 欲生成的二维码内容包含&符号。请注意，已将&符号替换成@并加上英文括号。")
        text = text.replace('&', '(@)')

    base_url = 'https://cn.apihz.cn/api/ewm/api.php'
    params = {
        "id": 88888888,
        "key": 88888888,
        "text": text,
        "level": 5,
        "size": 10,
        "bjcolour": "#ffffff",
        "xscolour": "#000000"
    }

    try:
        response = requests.get(base_url, params=params, proxies={"http": None, "https": None})
        response.raise_for_status()

        # 返回二维码图片的URL
        return response.url

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
        return ""
    except requests.exceptions.RequestException as err:
        print(f"请求错误发生: {err}")
        return ""


def download_video(video_url: str, file_name: str):
    try:
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"视频下载完成: {file_name}")
        return file_name  # 返回文件保存路径
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP错误发生: {http_err}")
        return None
    except requests.exceptions.RequestException as err:
        logging.error(f"请求错误发生: {err}")
        return None


@tool
def download_videos_from_url(api_url: str, download_folder: str = config['download_vido_path']) -> list:
    """从指定的URL获取视频信息并下载视频到本地文件夹，返回本地文件路径列表"""

    downloaded_files = []

    try:
        # 发送HTTP GET请求
        response = requests.get(api_url, proxies={"http": None, "https": None})
        response.raise_for_status()

        data = response.json()

        if data.get('code') == 200:
            # 提取标题和视频信息
            title = data.get('title')
            videos = data.get('data', [])

            # 创建下载目录（如果不存在）
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            logging.info(f"开始下载 '{title}' 的视频...")

            # 下载视频
            for video_info in videos:
                for video in video_info['video_data']:
                    clarity = video['clarity']
                    video_url = video['video_url']
                    format_size = video['format_size']

                    # 获取文件名
                    file_name = os.path.join(download_folder, f"{title}_{clarity}_{format_size}.mp4")

                    # 下载视频并收集文件路径
                    saved_file_path = download_video(video_url, file_name)
                    if saved_file_path:
                        downloaded_files.append(saved_file_path)

            logging.info("所有视频下载完成。")

        else:
            logging.error(f"请求成功但返回数据异常，错误消息: {data.get('msg')}")

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP错误发生: {http_err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"请求错误发生: {err}")

    return downloaded_files  # 返回下载文件的路径列表