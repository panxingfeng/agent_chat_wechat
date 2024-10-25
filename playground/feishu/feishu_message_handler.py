import json
import re
from datetime import datetime
from flask import jsonify

from config.templates.data.bot import CHATBOT_PROMPT_DATA, BOT_DATA, AGENT_BOT_PROMPT_DATA
from playground.feishu.message_type_group import MessageTypeGroup
from playground.feishu.message_type_private import MessageTypePrivate
from playground.feishu.send_message import SendMessage
from server.client.loadmodel.Ollama.OllamaClient import OllamaClient

# 当前时间
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class FeishuMessageHandler:
    def __init__(self, feishu_user,):
        # 创建 client
        self.feishu_user = feishu_user
        self.chat_model = OllamaClient()
        # 存储已处理过的 message_id
        self.processed_messages = set()
        self.send_message_tool = SendMessage()
        self.message_type_private = MessageTypePrivate
        self.message_type_group = MessageTypeGroup

    def handle_message(self, event_data,event_type):
        if event_type == "im.message.receive_v1":
            message = event_data.get('message', {})
            message_id = message.get('message_id')
            chat_type = message.get('chat_type')
            query = json.loads(message.get('content', '{}')).get('text', '')
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
                                                    query=query,
                                                    user_name=user_name,
                                                    user_id=sender_id
                                                )},
                    {"role": "user", "content": query}
                ]

                response = self.chat_model.invoke(messages=messages).content

                message_params = self.message_type_private(
                    receive_id=sender_id,
                    receive_id_type="open_id"
                ).handle(response)

                self.send_message_tool.send_message(message_params=message_params)

                return jsonify({
                    "message": f"消息处理成功，来自用户 {user_name} 的消息已回复。",
                    "success": True
                })
            elif chat_type == "group":
                chat_id = message.get('chat_id')
                mentions = message.get('mentions')
                key_value = mentions[0].get('name', None)
                # 清除群聊消息中@聊天机器人携带类似@_user_1字眼的内容
                query = re.sub(r'@\w+', '', query)
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
                                                        query=query,
                                                    )},
                        {"role": "user", "content": query}
                    ]

                    response = self.chat_model.invoke(messages=messages).content

                    message_params = self.message_type_group(
                        query=query,
                        send_id = sender_id,
                        receive_id=chat_id,
                        receive_id_type="chat_id"
                    ).handle(response)

                    self.send_message_tool.send_message(message_params=message_params)

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
