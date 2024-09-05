import random
import re
import string


def get_url(message):
    start = message.find("(") + 1
    end = message.find(")")
    link = message[start:end]
    return link



def generate_random_filename(extension=".png", length=10):
    """生成随机文件名"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length)) + extension

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