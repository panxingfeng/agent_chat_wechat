import logging
import random
import re
import string

import mysql.connector

from config.config import DB_DATA

conn = mysql.connector.connect(
    host=DB_DATA.get("host"),
    user=DB_DATA.get("user"),
    password=DB_DATA.get("password"),
    database=DB_DATA.get("database")
)

def save_message_to_mysql(message_text: str, timestamp: str, table_name: str, user_name: str) -> str:
    global conn
    try:
        with conn.cursor() as cursor:
            # 创建表格（如果尚未存在）
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_name VARCHAR(255),
                    message_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            ''')

            # 如果提供了自定义时间戳，则使用它，否则使用默认的 CURRENT_TIMESTAMP
            if timestamp:
                cursor.execute(f'''
                    INSERT INTO {table_name} (user_name, message_text, timestamp) VALUES (%s, %s, %s)
                ''', (user_name, message_text, timestamp))
            else:
                cursor.execute(f'''
                    INSERT INTO {table_name} (user_name, message_text) VALUES (%s, %s)
                ''', (user_name, message_text))

        # 提交事务
        conn.commit()
        return "消息已成功保存到 MySQL 数据库。"

    except Exception as e:
        logging.error(f"将消息保存到 MySQL 时发生错误: {e}")
        return f"保存消息失败, 失败原因: {e}"

    finally:
        if conn:
            conn.close()


def get_url(message):
    try:
        start = message.find("(") + 1
        end = message.find(")")
        if start == 0 or end == -1 or start >= end:
            raise ValueError("未找到有效的 URL 或格式不正确")

        link = message[start:end]

        # 简单的 URL 验证，可以检查前缀
        if not (link.startswith("http://") or link.startswith("https://")):
            raise ValueError("提取的链接不是有效的 URL")

        return link

    except Exception as e:
        print(f"提取 URL 失败: {e}")
        return None  # 返回 None 或其他默认值


async def generate_random_filename(extension=".png", length=10):
    """生成随机文件名，并确保返回的是字符串"""
    try:
        # 生成随机字符的列表（字母和数字）
        characters = string.ascii_letters + string.digits

        # 生成随机文件名
        file_name = ''.join(random.choice(characters) for _ in range(length)) + extension

        # 使用 str() 确保返回的是字符串
        return str(file_name)
    except Exception as e:
        logging.error(f"生成文件名时出错: {e}")
        return None  # 出错时返回 None

def get_username_chatroom(message):
    """从消息中提取并返回 'in' 之前和 'ber' 之后内容的交集。"""
    match_before_in = re.search(r"^(.*?) in", message)
    content_before_in = match_before_in.group(1).strip() if match_before_in else ''

    match_after_ber = re.search(r"ber(.*?)(?=>>)", message)
    content_after_ber = match_after_ber.group(1).strip() if match_after_ber else ''

    words_before_in = set(content_before_in.split())
    words_after_ber = set(content_after_ber.split())

    intersection = words_before_in & words_after_ber

    return ' '.join(intersection)
