import re


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