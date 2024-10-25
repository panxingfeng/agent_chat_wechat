import json
import os

import requests
from requests_toolbelt import MultipartEncoder # 输入pip install requests_toolbelt 安装依赖库

from config.config import FEISHU_DATA

class MessageTypeGroup:
    """
    格式化群用户回复用户的消息的格式
    """
    def __init__(self,query,send_id,receive_id,receive_id_type):
        self.query = query
        self.send_id = send_id
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
        else:
            return self.text_message(message)

    def text_message(self,message):
        return {
            "receive_id": self.receive_id,
            "content": json.dumps({
                        "text": f"<at user_id=\"{self.send_id}\"></at> {message}",
                    }),
            "msg_type": "text",
            "receive_id_type": self.receive_id_type
        }

    def image_message(self,image_key):
        if image_key:
            return {
                "receive_id": self.receive_id,
                "content":json.dumps({
                        "zh_cn": {
                            "title":"生成的图像结果",
                            "content":[
                                [
                                    {
                                        "tag": "at",
                                        "user_id": self.send_id,
                                        "style": ["bold"]
                                    },
                                    {
                                        "tag": "text",
                                        "text":"描述信息:",
                                        "style": ["blob"]
                                    },
                                    {
                                        "tag": "text",
                                        "text":self.query,
                                        "style": ["underline"]
                                    }
                                ],
                                [{
                                    "tag":"img",
                                    "image_key":image_key
                                }]
                            ]
                        }
                    }),
                "msg_type":"post",
                "receive_id_type": self.receive_id_type
            }
        else:
            return None


def get_image_key(image_path):
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    form = {'image_type': 'message',
            'image': (open(image_path, 'rb'))}
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
