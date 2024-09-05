import asyncio
import json
import logging
import os

from langchain_community.document_loaders import CSVLoader, WebBaseLoader, PyMuPDFLoader, \
    UnstructuredWordDocumentLoader, UnstructuredExcelLoader, UnstructuredMarkdownLoader

# 获取当前脚本所在的目录
base_dir = os.path.dirname(os.path.abspath(__file__))
# 配置文件的路径
config_path = os.path.join(base_dir, "../../config/config.json")

# 读取配置文件
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

# 保存用户的激活码状态，包括剩余时间和当天的验证状态
user_activation_status = {}

# 保存用户名和文件路径的映射
user_file_mapping = {}

# 支持的文件类型及其对应的加载器
SUPPORTED_FILE_TYPES = {
    'url': WebBaseLoader,          # 处理 URL 类型的文档
    'pdf': PyMuPDFLoader,          # 处理 PDF 类型的文档
    'docx': UnstructuredWordDocumentLoader,  # 处理 DOCX 类型的文档
    'excel': UnstructuredExcelLoader,        # 处理 Excel 类型的文档
    'csv': CSVLoader,              # 处理 CSV 类型的文档
    'md': UnstructuredMarkdownLoader,        # 处理 Markdown 类型的文档
}


class Group_message:
    def __init__(self, user_id, user_name, core, bot_name, chatroom_name, current_time, logging):
        """
        初始化 Group_message 类

        :param user_id: 用户 ID
        :param user_name: 用户名
        :param core: 核心处理对象
        :param bot_name: 机器人名称
        :param chatroom_name: 群聊名称
        :param current_time: 当前时间
        :param logging: 日志记录器
        """
        self.user_id = user_id
        self.user_name = user_name
        self.core = core
        self.bot_name = bot_name
        self.chatroom_name = chatroom_name
        self.current_time = current_time
        self.logging = logging

    async def handle_message(self, user_message, bot):
        """
        处理收到的消息

        :param user_message: 用户发送的消息
        :param bot: 处理消息的机器人对象
        """
        self.logging.info(f"收到了群【{self.chatroom_name}】的用户【{self.user_name}】的消息【{user_message}】")
        await self.distribute_message(user_message, bot)

    async def distribute_message(self, user_message, bot):
        """
        消息的分发

        :param user_message: 用户发送的消息
        :param bot: 处理消息的机器人对象
        """
        # 如果消息中包含 "-h"，则回复帮助信息
        if "-h" in user_message:
            reply_message = config['chatroom-h']
            await self.core.send_msg(f"@{self.user_name} {reply_message}", to_username=self.user_id)
            return

        # 如果消息中提到机器人，则处理消息
        if f"@{self.bot_name}" in user_message:
            await self.handle_else_message(user_message, bot)

    async def handle_else_message(self, user_message, bot):
        """
        处理其他类型的消息

        :param user_message: 用户发送的消息
        :param bot: 处理消息的机器人对象
        """
        # 获取机器人的回复
        reply_content = await bot.run(query=user_message, user_id=self.user_id, user_name=self.user_name)
        # 发送机器人的回复
        await self.core.send_msg(f"@{self.user_name} {reply_content}", to_username=self.user_id)
        return True
