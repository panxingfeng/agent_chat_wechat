import asyncio
import json
import os

from langchain_community.document_loaders import CSVLoader, WebBaseLoader, PyMuPDFLoader, \
    UnstructuredWordDocumentLoader, UnstructuredExcelLoader, UnstructuredMarkdownLoader

base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "../../config/config.json")
with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

# 保存用户的激活码状态，包括剩余时间和当天的验证状态
user_activation_status = {}

# 保存用户名和文件路径的映射
user_file_mapping = {}

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    'url': WebBaseLoader,
    'pdf': PyMuPDFLoader,
    'docx': UnstructuredWordDocumentLoader,
    'excel': UnstructuredExcelLoader,
    'csv': CSVLoader,
    'md': UnstructuredMarkdownLoader,
}


class Private_message:
    def __init__(self, user_id, user_name, core, bot_name, current_time, logging):
        self.user_id = user_id
        self.user_name = user_name
        self.core = core
        self.bot_name = bot_name
        self.current_time = current_time
        self.logging = logging

    async def handle_message(self, user_message,bot):
        """处理接受到的消息"""
        await self.distribute_message(user_message, bot)

    async def distribute_message(self, user_message, bot):
        """消息的分发"""
        if "-h" in user_message:
            reply_message = config['single-h']
            await self.core.send_msg(reply_message, to_username=self.user_id)
            return
        else:
            await self.handle_text_message(user_message, bot)
            return


    async def handle_text_message(self, user_message, bot):
        """处理关于文本内容的消息"""
        reply_content = await bot.run(query=user_message, user_id=self.user_id, user_name=self.user_name)
        await self.core.send_msg(reply_content, to_username=self.user_id)
        return

