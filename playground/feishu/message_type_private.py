import json
import os
import subprocess

import requests
from requests_toolbelt import MultipartEncoder # 输入pip install requests_toolbelt 安装依赖库

from config.config import FEISHU_DATA

class MessageTypePrivate:
    """
    格式化用户回复用户的消息的格式
    """
    def __init__(self,receive_id,receive_id_type):
        self.receive_id = receive_id
        self.receive_id_type = receive_id_type

    def handle(self, message):
        # 获取文件扩展名并转换为小写
        _, file_extension = os.path.splitext(message)
        file_extension = file_extension.lower()

        if file_extension == ".png":
            # 假设返回是一个图片文件地址
            image_key = get_image_key(message)
            return self.image_message(image_key)
        elif file_extension == ".mp3":
            # 假设返回是音频文件地址
            audio_key = get_audio_key(message)
            return self.audio_message(audio_key)
        elif file_extension in [".txt", ".doc", ".pdf"]:
            # 假设为文本或文档文件的处理
            file_key = get_file_key(message)
            return self.file_message(file_key)
        elif file_extension in [".mp4"]:
            file_key = get_file_key(message)
            # 视频的封面图 可以设置一个固定的封面图,也可以不设置封面图
            image_path = None
            image_key = get_image_key(image_path)
            return self.vidio_message(file_key,image_key)
        else:
            return self.text_message(message)

    def text_message(self,message):
        return {
            "receive_id": self.receive_id,
            "content": json.dumps({
                        "text": message,
                    }),
            "msg_type": "text",
            "receive_id_type": self.receive_id_type
        }

    def image_message(self,image_key):
        if image_key:
            return {
                "receive_id": self.receive_id,
                "content":json.dumps({
                        "image_key": image_key,
                    }),
                "msg_type":"image",
                "receive_id_type": self.receive_id_type
            }
        else:
            return None

    def audio_message(self,audio_key):
        if audio_key:
            return {
                "receive_id": self.receive_id,
                "content":json.dumps({
                        "file_key": audio_key,
                    }),
                "msg_type":"audio",
                "receive_id_type": self.receive_id_type
            }
        else:
            return None

    def file_message(self,file_key):
        if file_key:
            return {
                "receive_id": self.receive_id,
                "content":json.dumps({
                        "file_key": file_key
                    }),
                "msg_type":"file",
                "receive_id_type": self.receive_id_type
            }
        else:
            return None

    def vidio_message(self,file_key,image_key):
        if file_key:
            return {
                "receive_id": self.receive_id,
                "content":json.dumps({
                        "file_key": file_key,
                        "image_key": image_key
                    }),
                "msg_type":"media",
                "receive_id_type": self.receive_id_type
            }
        else:
            return None

def get_image_key(image_path):
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    form = {'image_type': 'message',
            'image': (open(image_path, 'rb'))}  # 需要替换具体的path
    multi_form = MultipartEncoder(form)
    headers = {'Authorization': "Bearer " + FEISHU_DATA.get('tenant_access_token'),
               'Content-Type': multi_form.content_type}
    response = requests.request("POST", url, headers=headers, data=multi_form)
    # 解析 JSON 响应
    response_data = response.json()
    if response_data.get("code") == 0:  # 检查请求是否成功
        image_key = response_data['data']['image_key']
        return image_key
    else:
        print("Error:", response_data.get("msg"))
        return None


def get_audio_key(file_path):
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    file_name = os.path.basename(file_path)
    form = {
        'file_type': 'stream',
        'file_name': file_name,
        'file': (file_name, open(file_path, 'rb'), 'audio/mpeg')
    }

    multi_form = MultipartEncoder(form)
    headers = {'Authorization': "Bearer " + FEISHU_DATA.get('tenant_access_token'),
               'Content-Type': multi_form.content_type}

    response = requests.request("POST", url, headers=headers, data=multi_form)
    response_data = response.json()
    if response_data.get("code") == 0:  # 检查请求是否成功
        audio_key = response_data['data']['file_key']
        return audio_key
    else:
        print("Error:", response_data.get("msg"))
        return None

def get_file_key(file_path):
    global file_type,mime_type
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    file_name = os.path.basename(file_path)
    if ".pdf" in file_name:
        file_type = 'pdf'
        mime_type = 'application/pdf'  # mime值参考 https://www.w3school.com.cn/media/media_mimeref.asp
    elif ".doc" in file_name:
        file_type = 'doc'
        mime_type = 'application/msword'
    elif ".xls" in file_name:
        file_type = 'xls'
        mime_type = 'application/vnd.ms-excel'
    elif ".ppt" in file_name:
        file_type = 'ppt'
        mime_type = 'application/vnd.ms-powerpoint'
    elif ".mp4" in file_name:
        file_type = 'mp4'
        mime_type = 'video/mp4'

    form = {
        'file_type': file_type,
        'file_name': file_name,
        'file': (file_name, open(file_path, 'rb'), mime_type)
    }

    multi_form = MultipartEncoder(form)
    headers = {'Authorization': "Bearer " + FEISHU_DATA.get('tenant_access_token'),
               'Content-Type': multi_form.content_type}

    response = requests.request("POST", url, headers=headers, data=multi_form)
    response_data = response.json()
    if response_data.get("code") == 0:  # 检查请求是否成功
        file_key = response_data['data']['file_key']
        print(file_key)
        return file_key
    else:
        print("Error:", response_data.get("msg"))
        return None
