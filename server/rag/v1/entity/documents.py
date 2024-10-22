import json


class Documents:
    """
    用于读取已分好类的 JSON 格式文档。
    """
    def __init__(self, path: str = '') -> None:
        self.path = path

    def get_content(self):
        """
        读取 JSON 格式的文档内容。
        :return: JSON 文档的内容
        """
        with open(self.path, mode='r', encoding='utf-8') as f:
            content = json.load(f)
        return content
