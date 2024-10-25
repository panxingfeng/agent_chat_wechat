import json
import re
from datetime import datetime

import lark_oapi as lark
from flask import jsonify
from lark_oapi.api.im.v1 import *

from config.config import FEISHU_DATA
from config.templates.data.bot import CHATBOT_PROMPT_DATA, BOT_DATA, AGENT_BOT_PROMPT_DATA
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient

# 当前时间
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class FeishuMessageHandler:
    def __init__(self, feishu_user, log_level=lark.LogLevel.INFO):
        # 创建 client
        self.app_id = FEISHU_DATA.get('app_id')
        self.app_secret = FEISHU_DATA.get('app_secret')
        self.feishu_user = feishu_user
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(log_level) \
            .build()
        self.chat_model = OllamaClient()
        # 存储已处理过的 message_id
        self.processed_messages = set()

    def send_message(self, receive_id: str, msg_type: str, content: str, receive_id_type: str) -> dict:
        """
        发送消息给指定用户
        :param receive_id: 接收消息的用户 open_id
        :param msg_type: 消息类型, 比如 "text"
        :param content: 消息内容 (JSON 格式字符串)
        :param receive_id_type: ID 类型, 默认为 "open_id"
        :return: 发送结果（字典形式）
        """
        # 构造请求对象
        request = CreateMessageRequest.builder() \
            .receive_id_type(receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(receive_id)
                          .msg_type(msg_type)
                          .content(content)  # 将文本内容转换为JSON
                          .build()) \
            .build()

        # 发起请求
        response = self.client.im.v1.message.create(request)

        # 处理失败返回
        if not response.success():
            error_message = f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            lark.logger.error(error_message)
            return {"success": False, "error": error_message}

        # 处理业务结果
        result = lark.JSON.marshal(response.data, indent=4)
        lark.logger.info(result)
        return {"success": True, "data": result}

    def handle_message(self, event_data,event_type):
        if event_type == "im.message.receive_v1":
            message = event_data.get('message', {})
            message_id = message.get('message_id')
            chat_type = message.get('chat_type')
            content = json.loads(message.get('content', '{}')).get('text', '')
            sender_id = event_data.get('sender', {}).get('sender_id', {}).get('open_id')
            if chat_type == "p2p":
                # 检查是否已经处理过这条消息
                if message_id in self.processed_messages:
                    print(f"消息 {message_id} 已经处理过，跳过处理")
                    return {"success": False, "message": "消息已处理"}

                # 标记消息为已处理
                self.processed_messages.add(message_id)

                # 获取用户信息
                user_info = self.feishu_user.get_user_info_by_id(
                    user_id=sender_id,
                    user_id_type="open_id"
                )
                formatted_info = self.feishu_user.format_user_info(user_info.get("data", {}))
                user_name = formatted_info.get("name", "未知用户")

                messages = [
                    {"role": "system", "content": AGENT_BOT_PROMPT_DATA.get("description").format
                                                    (
                                                    name=BOT_DATA["agent"].get("name"),
                                                    capabilities=BOT_DATA["agent"].get("capabilities"),
                                                    welcome_message=BOT_DATA["agent"].get("default_responses").get("welcome_message"),
                                                    unknown_command=BOT_DATA["agent"].get("default_responses").get("unknown_command"),
                                                    language_support=BOT_DATA["agent"].get("language_support"),
                                                    current_time=current_time,
                                                    history=None,
                                                    query=content,
                                                    user_name=user_name,
                                                    user_id=sender_id
                                                )},
                    {"role": "user", "content": content}
                ]

                response = self.chat_model.invoke(messages=messages)

                self.send_message(
                    receive_id=sender_id,
                    msg_type="text",
                    content=json.dumps({
                        "text": response.content,
                    }),
                    receive_id_type="open_id"
                )

                return jsonify({
                    "message": f"消息处理成功，来自用户 {user_name} 的消息已回复。",
                    "success": True
                })
            elif chat_type == "group":
                chat_id = message.get('chat_id')
                mentions = message.get('mentions')
                key_value = mentions[0].get('name', None)
                # 清除群聊消息中@聊天机器人携带类似@_user_1字眼的内容
                content = re.sub(r'@\w+', '', content)
                if key_value == "智能体机器人":
                    # 检查是否已经处理过这条消息
                    if message_id in self.processed_messages:
                        return {"success": False, "message": "消息已处理"}

                    # 标记消息为已处理
                    self.processed_messages.add(message_id)

                    # 获取用户信息
                    user_info = self.feishu_user.get_user_info_by_id(
                        user_id=sender_id,
                        user_id_type="open_id"
                    )
                    formatted_info = self.feishu_user.format_user_info(user_info.get("data", {}))
                    user_name = formatted_info.get("name", "未知用户")

                    messages = [
                        {"role": "system", "content": CHATBOT_PROMPT_DATA.get("description").format(
                                                        name=BOT_DATA["chat"].get("name"),
                                                        capabilities=BOT_DATA["chat"].get("capabilities"),
                                                        welcome_message=BOT_DATA["chat"].get("default_responses").get("welcome_message"),
                                                        unknown_command=BOT_DATA["chat"].get("default_responses").get("unknown_command"),
                                                        language_support=BOT_DATA["chat"].get("language_support"),
                                                        history=None,
                                                        query=content,
                                                    )},
                        {"role": "user", "content": content}
                    ]

                    response = self.chat_model.invoke(messages=messages)

                    self.send_message(
                        receive_id=chat_id,
                        msg_type="text",
                        content=json.dumps({
                            "text": f"<at user_id=\"{sender_id}\"></at> {response.content}"
                        }),
                        receive_id_type="chat_id"
                    )

                    # 发送回复消息
                    return jsonify({
                        "message": f"消息处理成功，来自用户 {user_name} 的消息已回复。",
                        "success": True
                    })
                else:
                    return jsonify({
                        "message": f"消息处理失败",
                        "success": False
                    })

        elif event_type == "im.message.message_read_v1":
            return jsonify({
                "message": "消息已读",
                "success": True
            })
